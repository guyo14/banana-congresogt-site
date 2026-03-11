import os
import csv

def rename_photos():
    cwd = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(cwd, "../data/congressmen.csv")
    images_dir = os.path.join(cwd, "../public/congressmen")

    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        return

    if not os.path.exists(images_dir):
        print(f"Error: Images directory not found at {images_dir}")
        return

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            photo_url = row.get("photo_url")
            id_str = row.get("id")
            
            if photo_url and photo_url.strip() and id_str:
                original_filename = photo_url.split("/")[-1]
                extension = original_filename.split(".")[-1] if "." in original_filename else "jpg"
                new_filename = f"{id_str}.{extension}"
                
                old_path = os.path.join(images_dir, original_filename)
                new_path = os.path.join(images_dir, new_filename)
                
                if os.path.exists(old_path):
                    try:
                        os.rename(old_path, new_path)
                        print(f"Renamed {original_filename} to {new_filename}")
                    except Exception as e:
                        print(f"Failed to rename {original_filename}: {e}")
                else:
                    if not os.path.exists(new_path):
                        print(f"File not found: {old_path}")

if __name__ == "__main__":
    rename_photos()
