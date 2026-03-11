import os
import csv

def find_missing_photos():
    cwd = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(cwd, "../data/congressmen.csv")
    images_dir = os.path.join(cwd, "../public/congressmen")

    ids_in_csv = []
    
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
             if row.get("id"):
                 ids_in_csv.append((row["id"], row["first_name"], row["last_name"], row["photo_url"]))
    
    files = os.listdir(images_dir)
    found_ids = [os.path.splitext(f)[0] for f in files if os.path.isfile(os.path.join(images_dir, f))]

    missing = []
    
    for c_id, first_name, last_name, url in ids_in_csv:
        if c_id not in found_ids:
            missing.append(f"{c_id} ({first_name} {last_name}) [Original URL: {url}]")
    
    if len(missing) == 0:
        print("No missing photos!")
    else:
        print(f"There are {len(missing)} missing photos:")
        for m in missing:
            print(f"- {m}")
            
if __name__ == "__main__":
    find_missing_photos()
