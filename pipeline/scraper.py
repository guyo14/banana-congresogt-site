import asyncio
import bs4
import re
from datetime import datetime
from playwright.async_api import async_playwright
import unicodedata
from . import db
from .logger import Log

# Mapping from normalized profile strings to database IDs
BLOCK_MAP = {
    "bienestarnacional-bien": 17,
    "cabal-cabal": 2,
    "compromiso,renovacionyorden-creo": 6,
    "comunidadelefante-elefante": 3,
    "movimientopoliticowinaq-unidadrevolucionarianacionalguatemalteca-winaq-urng-maiz": 14,
    "partidoazul-azul": 16,
    "partidopoliticonosotros-nosotros": 13,
    "partidopoliticovisionconvalores-viva": 7,
    "partidounionista-pu": 9,
    "todos-todos": 5,
    "unidadnacionaldelaesperanza-une": 11,
    "valor-valor": 8,
    "vamosporunaguatemaladiferente-vamos": 4,
    "victoria-victoria": 12,
    "voluntad,oportunidadysolidaridad-vos": 10,
    "cambio-cambio": 15,
}

DISTRICT_MAP = {
    "altaverapaz": 1,
    "bajaverapaz": 2,
    "chimaltenango": 4,
    "chiquimula": 5,
    "distritocentral": 3,
    "elprogreso": 6,
    "escuintla": 7,
    "guatemala": 8,
    "huehuetenango": 9,
    "izabal": 10,
    "jalapa": 11,
    "jutiapa": 12,
    "listanacional": 13,
    "peten": 14,
    "quetzaltenango": 15,
    "quiche": 16,
    "retalhuleu": 17,
    "sacatepequez": 18,
    "sanmarcos": 19,
    "santarosa": 20,
    "solola": 21,
    "suchitepequez": 22,
    "totonicapan": 23,
    "zacapa": 24,
}

BASE_URL = "https://www.congreso.gob.gt"

def normalize_string(s):
    if not s:
        return ""
    # Lowercase
    s = s.lower()
    # Remove accents
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
               if unicodedata.category(c) != 'Mn')
    # Remove spaces
    s = s.replace(" ", "")
    return s

def remove_unnecessary_spaces(string):
    return " ".join(string.split())

def match_congressman(congressman_name, congressmen_dict):
    norm_name = normalize_string(congressman_name)

    if norm_name in congressmen_dict:
        return congressmen_dict[norm_name]

    return None

async def get_browser_context(p):
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return browser, context

async def fetch_sessions(session_start):
    """Fetches the list of recent sessions and stops when parsing historical sessions below session_start."""
    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        page = await context.new_page()
        
        try:
            await page.goto(f"{BASE_URL}/seccion_informacion_legislativa/votaciones_pleno")
            
            # Fetch all rows by changing pagination to All (-1)
            try:
                await page.select_option("select[name='congreso_asistencias_length']", value="-1")
                await asyncio.sleep(2)
            except Exception as e:
                Log.error(f"Failed to load ALL sessions using datatables dropdown: {e}")
                
            await page.wait_for_selector("table#congreso_asistencias tbody tr", timeout=10000)
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "html.parser")
            
            sessions = []
            tbody = soup.select_one("table#congreso_asistencias tbody")
            if not tbody: return []
            
            rows = tbody.find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 4:
                    link = cols[3].find("a")
                    session_id = None
                    if link and "href" in link.attrs:
                        match = re.search(r'/eventos_votaciones/(\d+)', link['href'])
                        if match:
                            try:
                                session_id = int(match.group(1))
                            except:
                                Log.error(f"Failed to parse session ID from '{link['href']}'")
                                continue
                        else:
                            Log.error(f"Failed to parse session ID from '{link['href']}'")
                            continue    

                    if session_id >= session_start:
                        raw_type = cols[0].text.strip().lower()
                        # Map to English enum immediately
                        type_map = {
                            "ordinaria": "ordinary",
                            "extraordinaria": "extraordinary",
                            "solemne": "solemn"
                        }
                        if raw_type not in type_map:
                            Log.error(f"Unknown session type '{raw_type}' for session {session_id}. Defaulting to 'ordinary'.")
                            session_type = "ordinary"
                        else:
                            session_type = type_map[raw_type]

                        number_text = cols[1].text.strip()
                        number = None
                        try:
                            number = int(number_text)
                        except:
                            Log.error(f"Failed to parse session number for {session_id}")
                            continue
                        
                        desc = cols[2].text.strip()
                        # Parse date from description
                        date_match = re.search(r'Fecha (\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})', desc)
                        session_date = None
                        if date_match:
                            try:
                                session_date = datetime.strptime(date_match.group(1), "%d/%m/%Y %H:%M:%S")
                            except:
                                Log.error(f"Failed to parse session date for {session_id}")
                                continue
                        
                        # Use mapped session_type.
                        sessions.append({
                            "id": session_id,
                            "type": session_type,
                            "session_number": number,
                            "start_date": session_date
                        })
                        Log.debug(f"fetch_{session_id} Added: {session_type} {number}")
                    else:
                        Log.debug(f"fetch_{session_id} skipped")
                else:
                    Log.error(f"Invalid session row found")
            await browser.close()
            return sessions
        except Exception as e:
            Log.error(f"Error fetching sessions wrapper: {e}")
            await browser.close()
            return []

async def fetch_voting_for_session(session_id):
    """Fetches the voting records within a specific session."""
    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        page = await context.new_page()

        try:
            await page.goto(f"{BASE_URL}/eventos_votaciones/{session_id}", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_selector("table#congreso_asistencias tbody tr", timeout=10000)
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "html.parser")

            voting_records = []
            tbody = soup.select_one("table#congreso_asistencias tbody")
            Log.debug(f"fetch_voting: tbody found={bool(tbody)}")
            if not tbody: return []

            rows = tbody.find_all("tr")
            Log.debug(f"fetch_voting: found {len(rows)} rows")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 5:
                    subject = cols[0].text.strip()

                    voting_timestamp = None
                    time_str = cols[2].text.strip()
                    if time_str == "×":
                        continue # Responsive datatable artifact
                    try:
                        voting_timestamp = datetime.strptime(time_str, "%d/%m/%Y %H:%M:%S")
                    except Exception as e:
                        Log.error(f"Failed parsing voting timestamp '{time_str}' for session {session_id}: {e}")

                    link = cols[4].find("a")
                    voting_id = None
                    if link and "href" in link.attrs:
                        match = re.search(r'/detalle_de_votacion/(\d+)/', link['href'])
                        if match:
                            voting_id = int(match.group(1))

                    if voting_id:
                        voting_records.append({
                            "id": voting_id,
                            "session_id": session_id,
                            "subject": subject,
                            "start_date": voting_timestamp
                        })
            await browser.close()
            return voting_records
        except Exception as e:
            Log.error(f"Error fetching voting for session {session_id}: {e}")
            await browser.close()
            return []

async def fetch_attendance(session_id, session_type_id, congressmen_dict):
    """Fetches attendance for a session and maps to congressmen IDs."""
    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        page = await context.new_page()
        
        try:
            url = f"{BASE_URL}/detalle_asistencias/{session_type_id}/{session_id}"
            await page.goto(url, wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_selector("table", timeout=10000)
            
            # Since the table uses pagination (DataTables), we might need to select "All" entries
            # Let's extract DataTables data directly using page evaluate if possible, 
            # or just parse the HTML. The HTML has pagination. Let's try to select 'Todo' or -1.
            try:
                await page.select_option("select[name='congreso_asistencias_length']", value="-1")
                await asyncio.sleep(2) # Wait for table to reload all rows
            except:
                pass # If it fails, maybe it's not paginated
            
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "html.parser")
            
            attendance_records = []
            tbody = soup.select_one("table#congreso_asistencias tbody")
            if not tbody:
                Log.error(f"No attendance found for session {session_id}")
                return []
            
            for row in tbody.find_all("tr"):
                cols = row.find_all("td")
                if len(cols) >= 4:
                    raw_name = cols[0].text.strip()
                    
                    status = None
                    if "PRESENTE" in cols[1].text: status = "present"
                    elif "AUSENTE" in cols[2].text: status = "absent"
                    elif "LICENCIA" in cols[3].text: status = "license"
                    
                    if not status:
                        Log.error(f"Unknown attendance status for '{raw_name}' in session {session_id}")
                        continue
                        
                    c_id = match_congressman(raw_name, congressmen_dict)
                    if c_id:
                        attendance_records.append({
                            "session_id": session_id,
                            "congressman_id": c_id,
                            "status": status
                        })
                    else:
                        Log.error(f"Unmatched congressman attendance for Name: '{raw_name}' in session {session_id}")
                else:
                    Log.error(f"Invalid attendance row for session {session_id}")
            await browser.close()
            return attendance_records
        except Exception as e:
            Log.error(f"Error fetching attendance for session {session_id}: {e}")
            await browser.close()
            return []

async def fetch_votes(voting_id, session_id, congressmen_dict):
    """Fetches votes for a given voting record and maps to congressmen IDs."""
    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        page = await context.new_page()

        try:
            url = f"{BASE_URL}/detalle_de_votacion/{voting_id}/{session_id}#gsc.tab=0"

            # Retry connection 3 times to mitigate ERR_HTTP2_PROTOCOL_ERROR
            for attempt in range(3):
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    await page.wait_for_selector(".nav-tabs", timeout=10000)
                    break
                except Exception as ex:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(2)

            await asyncio.sleep(2) # Initial DOM load wait

            html = await page.content()
            soup = bs4.BeautifulSoup(html, "html.parser")

            votes_records = []

            # The tabs are FAVOR, CONTRA, AUSENCIA, LICENCIA/EXCUSA
            tabs = [
                ("in_favor", "present", 0, "congreso_a_favor_length"),
                ("against", "present", 1, "congreso_contra_length"),
                ("absent", "absent", 2, "congreso_votos_nulos_length"),
                ("absent", "license", 3, "congreso_licencia_length")
            ]

            # Expand all 4 DataTables in parallel using Playwright
            tasks = []
            for _, _, _, select_name in tabs:
                tasks.append(page.select_option(f"select[name='{select_name}']", value="-1", force=True))

            try:
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(2.5) # Allow heavy headless browser rendering of DataTables globally
            except:
                pass

            # Reparse HTML after expanding all length selectors
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "html.parser")
            tab_panes = soup.select(".tab-content .tab-pane")
            if len(tab_panes) != 4:
                Log.error(f"Unexpected number of tabs for voting {voting_id} in session {session_id}")
                return []

            for vote_type, att_status, tab_index, select_name in tabs:
                pane = tab_panes[tab_index]
                # Find the table in this pane
                tbody = pane.find("tbody")
                if tbody:
                    for row in tbody.find_all("tr"):
                        cols = row.find_all("td")
                        if len(cols) >= 1:
                            raw_name = cols[0].text.strip()
                            c_id = match_congressman(raw_name, congressmen_dict)
                            if c_id:
                                votes_records.append({
                                    "voting_id": voting_id,
                                    "congressman_id": c_id,
                                    "vote_type": vote_type,
                                    "attendance_status": att_status
                                })
                            else:
                                Log.error(f"Unmatched congressman vote for Name: '{raw_name}' in voting {voting_id}")

            await browser.close()
            return votes_records
        except Exception as e:
            Log.error(f"Error fetching votes for {voting_id}: {e}")
            await browser.close()
            return []

async def load_attendance_data(congressmen_dict, sessions):
    for session in sessions:
        s_id = session["id"]
        Log.info(f"Fetching Attendance for Session {s_id}...")
        session_type = session["type"]
        if session_type == "ordinary":
            session_type_id = 1
        elif session_type == "extraordinary":
            session_type_id = 2
        elif session_type == "solemn":
            session_type_id = 3
        else:
            Log.error(f"Unknown session type '{session_type}' for session {s_id}. Falling back to 1 (ordinary).")
            session_type_id = 1 # Fallback just in case
        attendances = await fetch_attendance(s_id, session_type_id, congressmen_dict)
        if len(attendances) != 160:
            Log.error(f"Only {len(attendances)} of 160 congressmen found for session {s_id}")
        att_tuples = [(att["session_id"], att["congressman_id"], att["status"]) for att in attendances]
        if att_tuples:
            db.insert_attendance(att_tuples)

async def load_voting_data(congressmen_dict, sessions):
    for session in sessions:
        s_id = session["id"]
        Log.info(f"Fetching Voting for Session {s_id}...")
        voting_records = await fetch_voting_for_session(s_id)

        for v in voting_records:
            v_id = v["id"]
            db.insert_voting((v_id, s_id, v["subject"], v.get("start_date")))

            Log.info(f"Fetching Votes for Voting {v_id}...")
            votes = await fetch_votes(v_id, s_id, congressmen_dict)
            if len(votes) != 160:
                Log.error(f"Only {len(votes)} of 160 congressmen found for voting {v_id} in session {s_id}")
            vote_tuples = [(vote["voting_id"], vote["congressman_id"], vote["vote_type"], vote["attendance_status"]) for vote in votes]
            if vote_tuples:
                db.insert_votes(vote_tuples)

async def update_congressmen_info(congressmen_dict):
    """
    Visits the profile page of every active congressman and extracts the
    Block and District they represent.
    For now, it prints out the distinct strings so the user can map them.
    """
    Log.info("Extracting block and district for all congressmen sequentially...")
    unique_ids = list(set(congressmen_dict.values()))
    
    unique_blocks = set()
    unique_districts = set()

    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        
        for i, cid in enumerate(unique_ids, 1):
            page = await context.new_page()
            try:
                # 30s timeout, wait until page finishes loading
                await page.goto(f"{BASE_URL}/perfil_diputado/{cid}", wait_until="domcontentloaded", timeout=30000)
                # wait a little explicitly so we bypass cloudflare challenges
                await asyncio.sleep(0.5)
                html = await page.content()
                soup = bs4.BeautifulSoup(html, "html.parser")
                b, d = None, None
                
                block_a = soup.find('a', href=re.compile(r'/perfil_bloques/'))
                if block_a:
                    b = block_a.text.strip()
                    unique_blocks.add(b)
                    
                dist_th = soup.find('th', string=re.compile(r'Distrito al que\s*representa:'))
                if dist_th:
                    td = dist_th.find_next_sibling('td')
                    if td:
                        d = td.text.strip()
                        unique_districts.add(d)
                
                # Perform mapping and database update
                norm_b = normalize_string(b) if b else None
                norm_d = normalize_string(d) if d else None
                
                b_id = BLOCK_MAP.get(norm_b) if norm_b else None
                d_id = DISTRICT_MAP.get(norm_d) if norm_d else None
                
                if b and not b_id and (norm_b != "independiente-ind" or norm_b != "-"):
                    Log.error(f"Mapping missing for Block: '{b}' (normalized: '{norm_b}')")
                if d and not d_id:
                    Log.error(f"Mapping missing for District: '{d}' (normalized: '{norm_d}')")
                
                if (b_id or norm_b == "independiente-ind") or d_id:
                    db.update_congressman_profile(cid, b_id, d_id)
                    Log.debug(f"Updated {cid} -> Block: {b_id} | District: {d_id}")
                    
            except Exception as e:
                Log.error(f"Failed to fetch profile for {cid}: {e}")
            finally:
                await page.close()
                
            if i % 10 == 0:
                Log.info(f"Processed {i}/{len(unique_ids)} profiles...")
                
        await browser.close()
        
    Log.info("=== UNIQUE BLOCKS FOUND ===")
    for b in sorted(unique_blocks):
        Log.info(f" - {b}")
        
    Log.info("=== UNIQUE DISTRICTS FOUND ===")
    for d in sorted(unique_districts):
        Log.info(f" - {d}")


async def run_scraper(action="load_sessions", session_start=41168, log_level="INFO"):
    """
    Run the scraper with specified parameters.

    Args:
        action: Action to perform (all, load_congressmen, load_voting, load_attendance, update_congressmen)
        session_start: Start session ID for fetching
        log_level: Logging verbosity level (DEBUG, INFO, WARNING, ERROR)
    """
    Log.init_file()
    Log.set_level(log_level)

    Log.info("Fetching congressmen in memory from database...")
    congressmen_dict = db.get_congressmen_dict()
    if not congressmen_dict:
        Log.error("No congressmen found in the database. Please run with --action load_congressmen or all first.")
        return

    if action in ["all", "update_congressmen"]:
        await update_congressmen_info(congressmen_dict)
        return

    if action in ["all", "load_voting", "load_attendance", "load_sessions"]:
        Log.info("Fetching Recent Sessions...")
        sessions = await fetch_sessions(session_start=session_start)
        Log.debug(f"Fetched {len(sessions)} sessions. IDs: {[s['id'] for s in sessions]}")

        # In case we still need chronological processing for DB inserts
        sessions.sort(key=lambda x: x["id"])
        Log.info(f"Found {len(sessions)} Historical Sessions to crawl.")

        for session in sessions:
            s_id = session["id"]
            Log.info(f"Process Session {s_id}: {session['type']} - No.: {session['session_number']} - Date: {session['start_date']}")

            session_type = session["type"]
            db.insert_session((s_id, session_type, session["session_number"], session["start_date"]))

        if action in ["all", "load_attendance", "load_sessions"]:
            await load_attendance_data(congressmen_dict, sessions)

        if action in ["all", "load_voting", "load_sessions"]:
            await load_voting_data(congressmen_dict, sessions)

    Log.info("Crawl complete.")
