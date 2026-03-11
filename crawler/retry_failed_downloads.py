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
    
    # Identify failures (< 1KB)
    failed_ids = []
    files = os.listdir(out_dir)
    for f in files:
        path = os.path.join(out_dir, f)
        if os.path.getsize(path) < 1000:
            c_id = f.split(".")[0]
            failed_ids.append(c_id)
            os.remove(path)
            
    print(f"Found {len(failed_ids)} failed downloads: {failed_ids}")
    if not failed_ids:
        return
        
    tasks_data = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") in failed_ids and row.get("photo_url"):
                url = row["photo_url"]
                if not url.startswith("http"):
                    url = f"{BASE_URL}{url}"
                ext = url.split(".")[-1] if "." in url.split("/")[-1] else "jpg"
                out = os.path.join(out_dir, f"{row['id']}.{ext}")
                tasks_data.append((row["id"], url, out))

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        for c_id, url, out in tasks_data:
            print(f"Retrying sequentially for {c_id}...")
            # Bypass incapsula again for good measure
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
                        if os.path.getsize(out) > 1000:
                            print(f"[{c_id}] Success!")
                            break
                        else:
                            os.remove(out)
                            print(f"[{c_id}] Still blocked.")
                except Exception as e:
                    print(f"[{c_id}] Error: {e}")
                await asyncio.sleep(2)
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
