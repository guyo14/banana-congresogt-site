import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.congreso.gob.gt/detalle_de_votacion/50558/41339#gsc.tab=0", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_selector(".nav-tabs", timeout=10000)
        await asyncio.sleep(2)
        
        tables = [
            ("a_favor", "congreso_a_favor", "congreso_a_favor_length"),
            ("en_contra", "congreso_contra", "congreso_contra_length"),
            ("ausente", "congreso_votos_nulos", "congreso_votos_nulos_length"),
            ("licencia", "congreso_licencia", "congreso_licencia_length")
        ]
        
        total = 0
        for name, table_id, select_name in tables:
            # Trigger length expansion
            js = f'if (typeof jQuery !== "undefined") jQuery("select[name=\'{select_name}\']").val("-1").trigger("change");'
            await page.evaluate(js)
            await asyncio.sleep(1)
            
            # Count rows
            rows = await page.evaluate(f'document.querySelectorAll("#{table_id} tbody tr").length')
            print(f"{name} rows: {rows}")
            total += rows
            
        print(f"Total: {total}")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
