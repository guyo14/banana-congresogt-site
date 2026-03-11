import asyncio
import bs4
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            # Go to finder to pass incapsula
            await page.goto("https://www.congreso.gob.gt/buscador_diputados", wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)
            
            # Now go to profile
            await page.goto("https://www.congreso.gob.gt/perfil_diputado/929", wait_until="domcontentloaded", timeout=20000)
            await asyncio.sleep(2)
            html = await page.content()
            
            soup = bs4.BeautifulSoup(html, "html.parser")
            imgs = soup.find_all("img")
            for img in imgs:
                src = img.get("src")
                if src and "diputado" in src:
                    print(src)
                
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
