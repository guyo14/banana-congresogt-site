import asyncio
import csv
import os
import traceback
from playwright.async_api import async_playwright

BASE_URL = "https://www.congreso.gob.gt"

async def fetch_image(context, c_id, url, out_path):
    for attempt in range(3):
        try:
            response = await context.request.get(url, timeout=15000)
            if response.status == 200:
                data = await response.body()
                with open(out_path, 'wb') as f:
                    f.write(data)
                print(f"[{c_id}] Saved {url}")
                return True
        except Exception as e:
            pass
        await asyncio.sleep(1)
    print(f"[{c_id}] Failed to download {url}")
    return False

async def main():
    cwd = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(cwd, "../data/congressmen.csv")
    out_dir = os.path.join(cwd, "../public/congressmen")
    os.makedirs(out_dir, exist_ok=True)
    
    tasks_data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") and row.get("photo_url"):
                url = row["photo_url"]
                if not url.startswith("http"):
                    url = f"{BASE_URL}{url}"
                ext = url.split(".")[-1] if "." in url.split("/")[-1] else "jpg"
                out = os.path.join(out_dir, f"{row['id']}.{ext}")
                tasks_data.append((row["id"], url, out))
    
    print(f"Starting concurrent downloads for {len(tasks_data)} images...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Bypass incapsula
        try:
            await page.goto(f"{BASE_URL}/buscador_diputados", wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(3)
        except Exception:
            pass
            
        sem = asyncio.Semaphore(10) # 10 concurrent requests
        
        async def bounded_fetch(c_id, url, out):
            async with sem:
                await fetch_image(context, c_id, url, out)
                
        tasks = [bounded_fetch(c_id, url, out) for c_id, url, out in tasks_data]
        await asyncio.gather(*tasks)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
