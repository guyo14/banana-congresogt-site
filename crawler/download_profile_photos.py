import asyncio
import bs4
import csv
import os
import urllib.request
import traceback
from playwright.async_api import async_playwright

BASE_URL = "https://www.congreso.gob.gt"

async def scrape_profiles():
    cwd = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(cwd, "../data/congressmen.csv")
    out_dir = os.path.join(cwd, "../public/congressmen")
    os.makedirs(out_dir, exist_ok=True)
    
    ids_to_fetch = []
    if os.path.exists(csv_path):
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("id"):
                    ids_to_fetch.append(row["id"])
    
    print(f"Found {len(ids_to_fetch)} IDs to fetch.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Bypass incapsula once
        try:
            await page.goto(f"{BASE_URL}/buscador_diputados", wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
        except Exception as e:
            print(f"Initial bypass error: {e}")

        for c_id in ids_to_fetch:
            print(f"Fetching profile for {c_id}...")
            target_url = None
            
            # Retry loop
            for attempt in range(3):
                try:
                    profile_url = f"{BASE_URL}/perfil_diputado/{c_id}"
                    await page.goto(profile_url, wait_until="domcontentloaded", timeout=20000)
                    await asyncio.sleep(1) # wait for DOM settling
                    html = await page.content()
                    soup = bs4.BeautifulSoup(html, "html.parser")
                    
                    # Image heuristic: look for assets/uploads/diputados
                    imgs = soup.find_all("img")
                    for img in imgs:
                        src = img.get("src", "")
                        if "assets/uploads/diputados" in src:
                            target_url = src
                            if not target_url.startswith("http"):
                                target_url = f"{BASE_URL}{target_url}"
                            break
                    
                    if not target_url:
                        for img in imgs:
                            src = img.get("src", "")
                            if "perfil" in src.lower() or "diputado" in src.lower():
                                target_url = src
                                if not target_url.startswith("http"):
                                    target_url = f"{BASE_URL}{target_url}"
                                break
                    break # Success, break retry loop!
                except Exception as e:
                    print(f"Attempt {attempt+1} error reading profile {c_id}: {e}")
                    await asyncio.sleep(2)
                
            if target_url:
                ext = target_url.split(".")[-1] if "." in target_url.split("/")[-1] else "jpg"
                out_path = os.path.join(out_dir, f"{c_id}.{ext}")
                try:
                    response = await page.request.get(target_url)
                    data = await response.body()
                    with open(out_path, 'wb') as out_file:
                        out_file.write(data)
                    print(f"Saved {target_url} to {c_id}.{ext}")
                except Exception as e:
                    print(f"Failed to download {target_url} for {c_id}: {e}")
            else:
                print(f"Could not find photo URL on profile {c_id}")
                
        await browser.close()

if __name__ == "__main__":
    try:
        asyncio.run(scrape_profiles())
    except Exception as e:
        traceback.print_exc()
