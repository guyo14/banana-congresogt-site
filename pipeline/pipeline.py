from . import db, scraper, transform_data
from .logger import Log

async def run_pipeline():
    Log.info(f"Starting pipeline")
    session_id = db.get_last_session()
    Log.info(f"Last session registered: {session_id}")

    Log.info("Running scraper...")
    if session_id is None:
        await scraper.run_scraper()
    else:
        await scraper.run_scraper(session_start=session_id + 1)

    Log.info("Running data transformation...")
    transform_data.run_transform()

    Log.info(f"Pipeline completed")
