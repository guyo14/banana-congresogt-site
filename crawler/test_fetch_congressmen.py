import asyncio
import json
from playwright.async_api import async_playwright

async def get_congressmen():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Go to main page to get Incapsula cookie
        await page.goto("https://www.congreso.gob.gt/buscador_diputados", wait_until="domcontentloaded", timeout=15000)
        
        # Wait a sec for protection
        await asyncio.sleep(2)
        
        # Execute fetch inside the browser environment
        result = await page.evaluate('''async () => {
            const response = await fetch("https://www.congreso.gob.gt/ctrl_website/finder_diputies", { 
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
        return result

async def main():
    result = await get_congressmen()
    try:
        data = json.loads(result)
        print(f"Got {len(data)} congressmen.")
        if len(data) > 0:
            print("First:", data[0])
            with open("congressmen.json", "w") as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print("Failed to parse JSON")
        print("Raw response:", result[:500])

if __name__ == "__main__":
    asyncio.run(main())
