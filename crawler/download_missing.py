import asyncio
import csv
import os
import traceback
from playwright.async_api import async_playwright

BASE_URL = "https://www.congreso.gob.gt"

async def main():
    cwd = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(cwd, "../data/congressmen.csv")
    out_dir = os.path.join(cwd, "../public/congressmen")
    
    # Identify completely missing
    existing_ids = [f.split(".")[0] for f in os.listdir(out_dir)]
    
    tasks_data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") and row["id"] not in existing_ids and row.get("photo_url"):
                url = row["photo_url"]
                if not url.startswith("http"):
                    url = f"{BASE_URL}{url}"
                ext = url.split(".")[-1] if "." in url.split("/")[-1] else "jpg"
                out = os.path.join(out_dir, f"{row['id']}.{ext}")
                tasks_data.append((row["id"], url, out))

    print(f"Found {len(tasks_data)} missing downloads.")
    if not tasks_data:
        return

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for c_id, url, out in tasks_data:
            print(f"Fetching {c_id} (Timeout 60s)...")
            try:
                await page.goto(f"{BASE_URL}/buscador_diputados", wait_until="domcontentloaded", timeout=15000)
                await asyncio.sleep(2)
            except Exception:
                pass
                
            for attempt in range(3):
                try:
                    response = await page.request.get(url, timeout=60000)
                    if response.status == 200:
                        data = await response.body()
                        with open(out, 'wb') as f:
                            f.write(data)
                        print(f"[{c_id}] Success!")
                        break
                    else:
                        print(f"[{c_id}] Status {response.status}")
                except Exception as e:
                    print(f"[{c_id}] Error: {e}")
                await asyncio.sleep(2)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
