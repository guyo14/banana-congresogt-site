import sys
import argparse
import asyncio
from pipeline import scraper, transform_data, db_initializer, pipeline


def main():
    """Entry point for the congressional data pipeline."""
    parser = argparse.ArgumentParser(
        description="Congressional Data Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Scraper subcommand
    scrape_parser = subparsers.add_parser('scrape', help='Scrape congressional data from the web')
    scrape_parser.add_argument(
        '--action',
        choices=['all', 'load_congressmen', 'load_voting', 'load_attendance', 'update_congressmen', 'load_sessions'],
        default='load_sessions',
        help='Action to perform (default: load_sessions)'
    )
    scrape_parser.add_argument(
        '--session-start',
        type=int,
        default=41168,
        help='Start session ID for fetching (default: 41168)'
    )
    scrape_parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set the logging verbosity level (default: INFO)'
    )

    # Transform subcommand
    subparsers.add_parser('transform', help='Transform raw data and generate statistics')

    # Initialize database subcommand
    subparsers.add_parser('db', help='Initialize the database with raw data from the backup')

    # Pipeline subcommand (runs export + transform)
    subparsers.add_parser('pipeline', help='Run the full pipeline (export + transform)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    if args.command == 'scrape':
        asyncio.run(scraper.run_scraper(
            action=args.action,
            session_start=args.session_start,
            log_level=args.log_level
        ))

    elif args.command == 'transform':
        transform_data.run_transform()

    elif args.command == 'db':
        db_initializer.initialize_db()

    elif args.command == 'pipeline':
        asyncio.run(pipeline.run_pipeline())

    return 0


if __name__ == "__main__":
    sys.exit(main())
