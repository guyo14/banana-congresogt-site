import sys
import datetime
import os

class Log:
    LOG_FILE = "crawl_report.txt"
    LEVELS = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40}
    current_level = 20  # Default to INFO

    @classmethod
    def set_level(cls, level_str):
        cls.current_level = cls.LEVELS.get(level_str.upper(), 20)

    @classmethod
    def _write(cls, level, message):
        # Skip if below current verbosity
        if cls.LEVELS.get(level, 0) < cls.current_level:
            return
            
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted = f"[{timestamp}] [{level}] {message}"
        
        # Standard output
        print(formatted)
        
        # Write ERRORs to file
        if level == "ERROR":
            try:
                with open(cls.LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(formatted + "\n")
            except Exception as e:
                print(f"[Log] Failed to write to {cls.LOG_FILE}: {e}", file=sys.stderr)

    @classmethod
    def debug(cls, message):
        cls._write("DEBUG", message)

    @classmethod
    def info(cls, message):
        cls._write("INFO", message)

    @classmethod
    def warn(cls, message):
        cls._write("WARNING", message)

    @classmethod
    def error(cls, message):
        cls._write("ERROR", message)

    @classmethod
    def init_file(cls):
        """Initializes/clears the log file for a new execution."""
        try:
            with open(cls.LOG_FILE, "w", encoding="utf-8") as f:
                f.write(f"--- Crawl Report Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        except Exception as e:
            print(f"[Log] Failed to initialize {cls.LOG_FILE}: {e}", file=sys.stderr)
