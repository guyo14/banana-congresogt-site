import asyncio
from playwright.async_api import async_playwright
import bs4

async def main():
    url = "https://www.congreso.gob.gt/eventos_votaciones/41339"
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=20000)
        await asyncio.sleep(2)
        html = await page.content()
        soup = bs4.BeautifulSoup(html, "html.parser")
        
        tables = soup.find_all("table")
        for i, t in enumerate(tables):
            print(f"Table {i} ID: {t.get('id')}")
            rows = t.find_all("tr")
            print(f"  Rows: {len(rows)}")
            for r in rows[:2]:
                print(f"    Cols: {len(r.find_all('td'))}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
