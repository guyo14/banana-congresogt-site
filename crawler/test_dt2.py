import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.congreso.gob.gt/detalle_de_votacion/50558/41339#gsc.tab=0", wait_until="domcontentloaded", timeout=20000)
        await page.wait_for_selector(".nav-tabs", timeout=10000)
        await asyncio.sleep(2) # Baseline wait for tables to init
        
        # Trigger ALL tables using DataTables API simultaneously
        js = """
        if (typeof jQuery !== 'undefined' && jQuery.fn.dataTable) {
            // Find all tables that have a DataTable instance and expand them
            jQuery('.table').each(function() {
                if (jQuery.fn.dataTable.isDataTable(this)) {
                    jQuery(this).DataTable().page.len(-1).draw();
                }
            });
        }
        """
        await page.evaluate(js)
        await asyncio.sleep(1) # Wait once for redrawing
        
        tables = [
            ("a_favor", "congreso_a_favor"),
            ("en_contra", "congreso_contra"),
            ("ausente", "congreso_votos_nulos"),
            ("licencia", "congreso_licencia")
        ]
        
        total = 0
        for name, table_id in tables:
            rows = await page.evaluate(f'document.querySelectorAll("#{table_id} tbody tr").length')
            print(f"{name} rows: {rows}")
            total += rows
            
        print(f"Total: {total}")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
