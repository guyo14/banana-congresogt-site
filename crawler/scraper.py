import asyncio
import json
import bs4
import re
import argparse
from datetime import datetime
from playwright.async_api import async_playwright
import db
from logger import Log

BASE_URL = "https://www.congreso.gob.gt"

async def get_browser_context(p):
    browser = await p.chromium.launch(headless=True)
    context = await browser.new_context(
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return browser, context

async def fetch_congressmen():
    """Fetches the master list of congressmen from the JSON API."""
    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        page = await context.new_page()
        
        # Get Incapsula clearance by visiting the directory page first
        try:
            await page.goto(f"{BASE_URL}/buscador_diputados", wait_until="domcontentloaded", timeout=15000)
            await asyncio.sleep(2)
        except:
            pass
            
        result = await page.evaluate('''async () => {
            const response = await fetch("/ctrl_website/finder_diputies", { 
                method: "POST", 
                body: JSON.stringify({"target": ""}),
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest"
                }
            });
            return await response.text();
        }''')
        
        await browser.close()
        
        try:
            data = json.loads(result)
            return data
        except:
            Log.error("Failed to fetch congressmen JSON.")
            return []

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
                        type = cols[0].text.strip()
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
                        
                        # Use raw tipo instead of mapped IDs.
                        sessions.append({
                            "id": session_id,
                            "type": type,
                            "session_number": number,
                            "start_date": session_date
                        })
                        Log.debug(f"fetch_{session_id} Added: {type} {number}")
                    else:
                        Log.debug(f"fetch_{session_id} Skipped: {type} {number}")
                else:
                    Log.error(f"Invalid session row found")
            await browser.close()
            return sessions
        except Exception as e:
            Log.error(f"Error fetching sessions wrapper: {e}")
            await browser.close()
            return []

async def fetch_votations_for_session(session_id):
    """Fetches the votations within a specific session."""
    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        page = await context.new_page()
        
        try:
            await page.goto(f"{BASE_URL}/eventos_votaciones/{session_id}", wait_until="domcontentloaded", timeout=15000)
            await page.wait_for_selector("table#congreso_asistencias tbody tr", timeout=10000)
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "html.parser")
            
            votations = []
            tbody = soup.select_one("table#congreso_asistencias tbody")
            Log.debug(f"fetch_votations: tbody found={bool(tbody)}")
            if not tbody: return []
            
            rows = tbody.find_all("tr")
            Log.debug(f"fetch_votations: found {len(rows)} rows")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 5:
                    subject = cols[0].text.strip()
                    
                    votation_timestamp = None
                    time_str = cols[2].text.strip()
                    if time_str == "×":
                        continue # Responsive datatable artifact
                    try:
                        votation_timestamp = datetime.strptime(time_str, "%d/%m/%Y %H:%M:%S")
                    except Exception as e:
                        Log.error(f"Failed parsing votation timestamp '{time_str}' for session {session_id}: {e}")
                    
                    link = cols[4].find("a")
                    votation_id = None
                    if link and "href" in link.attrs:
                        match = re.search(r'/detalle_de_votacion/(\d+)/', link['href'])
                        if match:
                            votation_id = int(match.group(1))
                            
                    if votation_id:
                        votations.append({
                            "id": votation_id,
                            "session_id": session_id,
                            "subject": subject,
                            "start_date": votation_timestamp
                        })
            await browser.close()
            return votations
        except Exception as e:
            Log.error(f"Error fetching votations for session {session_id}: {e}")
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
                    if "PRESENTE" in cols[1].text: status = "presente"
                    elif "AUSENTE" in cols[2].text: status = "ausente"
                    elif "LICENCIA" in cols[3].text: status = "licencia_excusa"
                    
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

async def fetch_votes(votation_id, session_id, congressmen_dict):
    """Fetches votes for a given votation and maps to congressmen IDs."""
    async with async_playwright() as p:
        browser, context = await get_browser_context(p)
        page = await context.new_page()
        
        try:
            url = f"{BASE_URL}/detalle_de_votacion/{votation_id}/{session_id}#gsc.tab=0"
            
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
                ("a_favor", "presente", 0, "congreso_a_favor_length"),
                ("en_contra", "presente", 1, "congreso_contra_length"),
                ("ausente", "ausente", 2, "congreso_votos_nulos_length"),
                ("ausente", "licencia_excusa", 3, "congreso_licencia_length")
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

            # Re-parse HTML after expanding all length selectors
            html = await page.content()
            soup = bs4.BeautifulSoup(html, "html.parser")
            tab_panes = soup.select(".tab-content .tab-pane")
            if len(tab_panes) != 4:
                Log.error(f"Unexpected number of tabs for votation {votation_id} in session {session_id}")
                return []

            for vote_type, att_status, tab_index, select_name in tabs:
                pane = tab_panes[tab_index]
                # Find table in this pane
                tbody = pane.find("tbody")
                if tbody:
                    for row in tbody.find_all("tr"):
                        cols = row.find_all("td")
                        if len(cols) >= 1:
                            raw_name = cols[0].text.strip()
                            c_id = match_congressman(raw_name, congressmen_dict)
                            if c_id:
                                votes_records.append({
                                    "votation_id": votation_id,
                                    "congressman_id": c_id,
                                    "vote_type": vote_type,
                                    "attendance_status": att_status
                                })
                            else:
                                Log.error(f"Unmatched congressman vote for Name: '{raw_name}' in votation {votation_id}")
                                    
            await browser.close()
            return votes_records
        except Exception as e:
            Log.error(f"Error fetching votes for {votation_id}: {e}")
            await browser.close()
            return []

def remove_unnecessary_spaces(string):
    return " ".join(string.split())

def normalize_name(name):
    # Normalizing by lowercasing and removing extra spaces for matching.
    return remove_unnecessary_spaces(name).lower()

def match_congressman(congressman_name, congressmen_dict):
    norm_name = normalize_name(congressman_name)
    
    if norm_name in congressmen_dict:
        return congressmen_dict[norm_name]

    return None

async def load_congressmen_data():
    Log.info("Fetching Master Congressmen List...")
    congressmen_raw = await fetch_congressmen()
    congressmen_dict = {}
    congressmen_tuples = []
    parties = {}
    districts = {}
    
    for c in congressmen_raw:
        c_id = int(c["id_diputado"])
        first_name = remove_unnecessary_spaces(c['nombres'])
        last_name = remove_unnecessary_spaces(c['apellidos'])
        key = f"{last_name} {first_name}".lower()
        
        photo = c.get("foto_perfil", "")
        photo_url = f"{BASE_URL}/assets/uploads/diputados/{photo}" if photo else ""
        birth_date = None
        if "fecha_nacimiento" in c and c["fecha_nacimiento"] and c["fecha_nacimiento"] != "0000-00-00":
            birth_date = c["fecha_nacimiento"]
            
        p_id = None
        if c.get("id_bloque"):
            try: p_id = int(c["id_bloque"])
            except:
                Log.error(f"Invalid party ID for congressman {c_id}")
                continue
            parties[p_id] = parties[p_id] if p_id in parties and parties[p_id] else c["nombre_bloque"]
            
        d_id = None
        if c.get("id_distrito"):
            try: d_id = int(c["id_distrito"])
            except:
                Log.error(f"Invalid district ID for congressman {c_id}")
                continue
            districts[d_id] = districts[d_id] if d_id in districts and districts[d_id] else c["nombre_distrito"]
        
        congressmen_dict[key] = c_id
        congressmen_tuples.append((c_id, first_name, last_name, key, p_id, d_id, photo_url, birth_date, 'active'))
    
    if parties:
        for party_id, party_name in parties.items():
            if not party_name:
                Log.error(f"Invalid party name for party ID {party_id}")
                parties[party_id] = "Unknown"
        Log.info(f"Inserting {len(parties)} parties.")
        db.insert_parties(list(parties.items()))
    if districts:
        for district_id, district_name in districts.items():
            if not district_name:
                Log.error(f"Invalid district name for district ID {district_id}")
                districts[district_id] = "Unknown"
        Log.info(f"Inserting {len(districts)} districts.")
        db.insert_districts(list(districts.items()))
    Log.info(f"Inserting {len(congressmen_tuples)} congressmen.")
    db.insert_congressmen(congressmen_tuples)
    return congressmen_dict

async def load_attendance_data(congressmen_dict, sessions):
    for session in sessions:
        s_id = session["id"]
        Log.info(f"Fetching Attendance for Session {s_id}...")
        session_type = session["type"].lower()
        if session_type == "ordinaria":
            session_type_id = 1
        elif session_type == "extraordinaria":
            session_type_id = 2
        elif session_type == "solemne":
            session_type_id = 3
        else:
            Log.error(f"Unknown session type '{session_type}' for session {s_id}. Falling back to 1 (ordinaria).")
            session_type_id = 1 # Fallback just in case
        attendances = await fetch_attendance(s_id, session_type_id, congressmen_dict)
        if len(attendances) != 160:
            Log.error(f"Only {len(attendances)} of 160 congressmen found for session {s_id}")
        att_tuples = [(att["session_id"], att["congressman_id"], att["status"]) for att in attendances]
        if att_tuples:
            db.insert_attendance(att_tuples)

async def load_votations_data(congressmen_dict, sessions):
    for session in sessions:
        s_id = session["id"]
        Log.info(f"Fetching Votations for Session {s_id}...")
        votations = await fetch_votations_for_session(s_id)
        
        for v in votations:
            v_id = v["id"]
            db.insert_votation((v_id, s_id, v["subject"], v.get("start_date")))
            
            Log.info(f"Fetching Votes for Votation {v_id}...")
            votes = await fetch_votes(v_id, s_id, congressmen_dict)
            if len(votes) != 160:
                Log.error(f"Only {len(votes)} of 160 congressmen found for votation {v_id} in session {s_id}")
            vote_tuples = [(vote["votation_id"], vote["congressman_id"], vote["vote_type"], vote["attendance_status"]) for vote in votes]
            if vote_tuples:
                db.insert_votes(vote_tuples)

async def main():
    Log.init_file()
    parser = argparse.ArgumentParser(description="Congress Data Crawler")
    parser.add_argument("--action", choices=["all", "load_congressmen", "load_votations", "load_attendance"], default="all", help="Action to perform")
    parser.add_argument("--session-start", type=int, default=41168, help="Start session ID for fetching (default: 41168)")
    parser.add_argument("--log-level", choices=["DEBUG", "INFO", "WARNING", "ERROR"], default="INFO", help="Set the logging verbosity level (default: INFO)")
    args = parser.parse_args()

    # Apply configuration to logger
    Log.set_level(args.log_level)

    # Initialize DB (run schema.sql IF NOT EXISTS)
    db.init_db()
    
    # We always need the congressmen_dict to match names to IDs.
    if args.action in ["load_congressmen"]:
        congressmen_dict = await load_congressmen_data()
        db.init_aliases()
        return
    
    Log.info("Fetching congressmen in memory from database...")
    congressmen_dict = db.get_congressmen_dict()
    if not congressmen_dict:
        Log.error("No congressmen found in the database. Please run with --action load_congressmen or all first.")
        return

    if args.action in ["all", "load_votations", "load_attendance"]:
        Log.info("Fetching Recent Sessions...")
        sessions = await fetch_sessions(session_start=args.session_start)
        Log.debug(f"Fetched {len(sessions)} sessions. IDs: {[s['id'] for s in sessions]}")

        # In case we still need chronological processing for DB inserts
        sessions.sort(key=lambda x: x["id"])
        Log.info(f"Found {len(sessions)} Historical Sessions to crawl.")
        
        for session in sessions:
            s_id = session["id"]
            Log.info(f"Process Session {s_id}: {session['type']} - No.: {session['session_number']} - Date: {session['start_date']}")
            
            # Map unrecognized sessions to 'ordinaria' to fit enum, but we already warn later in attendance
            session_type = session["type"].lower()
            if session_type not in ["ordinaria", "extraordinaria", "solemne"]:
                Log.error(f"Unknown session type '{session_type}' for session {s_id}. Defaulting to 'ordinaria' for DB enum constraint.")
                session_type = "ordinaria"

            db.insert_session((s_id, session_type, session["session_number"], session["start_date"]))
            
        if args.action in ["all", "load_attendance"]:
            await load_attendance_data(congressmen_dict, sessions)
            
        if args.action in ["all", "load_votations"]:
            await load_votations_data(congressmen_dict, sessions)

    Log.info("Crawl complete.")

if __name__ == "__main__":
    asyncio.run(main())
