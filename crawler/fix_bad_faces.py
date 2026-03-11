import os
import cv2

def fix_problematic_faces():
    cwd = os.path.dirname(os.path.abspath(__file__))
    in_dir = os.path.join(cwd, "../public/congressmen-std")
    out_dir = os.path.join(cwd, "../public/face")
    
    os.makedirs(out_dir, exist_ok=True)
    
    bad_ids = [
        '18', '31', '86', '117', '247', '772', '774', '785', '787', '796', 
        '864', '885', '887', '888', '893', '908', '915', '918', '919', '928', 
        '935', '953', '956', '959', '966', '969', '974'
    ]
    
    # We know images in congressmen-std are exactly 600x800
    # A standard ID photo face at 600x800 is comfortably within a 460x460 square 
    # slightly lowered from the very top (e.g. y offset 60, x offset 70)
    
    crop_size = 460
    x_offset = (600 - crop_size) // 2 # 70
    y_offset = 80 # Down from top to leave headroom
    
    target_w, target_h = 300, 300

    print(f"Fixing {len(bad_ids)} faces...")
    
    for c_id in bad_ids:
        filepath = os.path.join(in_dir, f"{c_id}.jpg")
        out_filepath = os.path.join(out_dir, f"{c_id}.jpg")
        
        if not os.path.exists(filepath):
            print(f"[{c_id}] Missing in std folder: {filepath}")
            continue
            
        try:
            img = cv2.imread(filepath)
            if img is None:
                print(f"[{c_id}] Failed to read image")
                continue
            
            # Use the reliable fixed crop instead of Haar Cascade
            face_img = img[y_offset:y_offset+crop_size, x_offset:x_offset+crop_size]
            
            # Resize exactly to target 300x300
            img_resized = cv2.resize(face_img, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            # Apply identical <100KB constraints
            quality = 95
            max_size = 100 * 1024
            
            while quality > 10:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                result, encimg = cv2.imencode('.jpg', img_resized, encode_param)
                
                if result:
                    if len(encimg) < max_size:
                        with open(out_filepath, 'wb') as f:
                            f.write(encimg)
                        print(f"[{c_id}] Saved fixed crop at quality {quality} ({len(encimg)/1024:.1f} KB)")
                        break
                    else:
                        quality -= 5
                else:
                    print(f"[{c_id}] Encoding failed")
                    break
        except Exception as e:
            print(f"[{c_id}] Error: {e}")

if __name__ == "__main__":
    fix_problematic_faces()
