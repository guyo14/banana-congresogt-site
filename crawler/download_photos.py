import os
import csv
import urllib.request

def download_photos():
    cwd = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(cwd, "../data/congressmen.csv")
    output_dir = os.path.join(cwd, "../public/diputados")

    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            photo_url = row.get("photo_url")
            id_str = row.get("id")
            
            if photo_url and photo_url.strip():
                filename = photo_url.split("/")[-1]
                local_path = os.path.join(output_dir, filename)
                
                # Download if it doesn't already exist
                if not os.path.exists(local_path):
                    try:
                        print(f"Downloading {filename}...")
                        
                        # Add User-Agent header to avoid 403 Forbidden
                        req = urllib.request.Request(
                            photo_url, 
                            data=None, 
                            headers={
                                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                            }
                        )
                        with urllib.request.urlopen(req) as response, open(local_path, 'wb') as out_file:
                            data = response.read()
                            out_file.write(data)
                    except Exception as e:
                        print(f"Failed to download {photo_url} for ID {id_str}: {e}")
                else:
                    print(f"Skipping {filename}, already exists.")

if __name__ == "__main__":
    download_photos()
