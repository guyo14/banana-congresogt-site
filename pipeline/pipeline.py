import os
import subprocess
import sys

def run_script(script_name):
    print(f"=========================================")
    print(f"Running {script_name}...")
    print(f"=========================================")
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    try:
        # Run the script using the same python executable
        subprocess.run([sys.executable, script_path], check=True)
        print(f"Successfully completed {script_name}.\n")
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_name}!")
        print(f"Exit code: {e.returncode}")
        sys.exit(e.returncode)

def main():
    print("Starting Data Pipeline Orchestration\n")
    
    # 1. Scrape data (Uncomment if needed, or pass arguments)
    # run_script("scraper.py")
    
    # 2. Export raw tables from Postgres to CSV
    run_script("export_backup.py")
    
    # 3. Transform data and generate advanced stats & similarity matrix
    run_script("transform_data.py")
    
    print("Pipeline finished successfully!")

if __name__ == "__main__":
    main()
