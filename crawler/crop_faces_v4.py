import os
import cv2

def crop_faces_uniform():
    cwd = os.path.dirname(os.path.abspath(__file__))
    in_dir = os.path.join(cwd, "../public/congressmen-std")
    out_dir = os.path.join(cwd, "../public/face")
    
    os.makedirs(out_dir, exist_ok=True)
    
    image_files = [f for f in os.listdir(in_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"Applying uniform square crop to {len(image_files)} images...")
    
    target_dim = 300
    
    for filename in image_files:
        filepath = os.path.join(in_dir, filename)
        id_str = os.path.splitext(filename)[0]
        out_filepath = os.path.join(out_dir, f"{id_str}.jpg")
        
        try:
            img = cv2.imread(filepath)
            if img is None:
                continue
                
            img_h, img_w = img.shape[:2]
            
            # Use a mathematically uniform square crop from the top portion 
            # of the 600x800 image. This captures the head and shoulders cleanly 
            # for standard ID photography without creeping in too closely.
            
            # Take the maximum square that fits the width, slightly down from top
            # For 600x800, this is a 600x600 square starting at y=20 or 0
            # We'll use a 600x600 square starting at y=0 (top edge) 
            # to be safe from chopping off tall hair/heads.
            
            side = min(img_w, img_h) # Should be 600
            
            y1 = 0 
            x1 = (img_w - side) // 2 # 0 if img_w == 600
            
            face_img = img[y1:y1+side, x1:x1+side]
            
            img_resized = cv2.resize(face_img, (target_dim, target_dim), interpolation=cv2.INTER_AREA)
            
            # Compression
            max_size = 100 * 1024
            
            for quality in range(95, 10, -5):
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                result, encimg = cv2.imencode('.jpg', img_resized, encode_param)
                if result and len(encimg) < max_size:
                    with open(out_filepath, 'wb') as f:
                        f.write(encimg)
                    print(f"[{id_str}] Saved quality {quality} ({len(encimg)/1024:.1f} KB)")
                    break
                    
        except Exception as e:
            print(f"[{id_str}] Failed: {e}")

if __name__ == "__main__":
    crop_faces_uniform()
