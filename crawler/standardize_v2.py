import os
import cv2
import numpy as np

def standardize_photos_v2():
    cwd = os.path.dirname(os.path.abspath(__file__))
    in_dir = os.path.join(cwd, "../public/congressmen")
    out_dir = os.path.join(cwd, "../public/congressmen-std")
    
    os.makedirs(out_dir, exist_ok=True)
    
    # 1. We need to find the dimensions of 95.jpg
    ref_path = os.path.join(in_dir, "95.jpg")
    if not os.path.exists(ref_path):
        print(f"Error: Reference image {ref_path} not found.")
        return
        
    ref_img = cv2.imread(ref_path)
    if ref_img is None:
        print(f"Error: Could not read {ref_path}")
        return
        
    target_h, target_w = ref_img.shape[:2]
    target_aspect = target_w / target_h
    print(f"Target dimensions: {target_w}x{target_h} (Aspect ratio: {target_aspect:.2f})")
    
    files = os.listdir(in_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"Processing {len(image_files)} images...")
    
    for filename in image_files:
        filepath = os.path.join(in_dir, filename)
        id_str = os.path.splitext(filename)[0]
        out_filepath = os.path.join(out_dir, f"{id_str}.jpg")
        
        try:
            img = cv2.imread(filepath)
            if img is None:
                print(f"[{id_str}] Failed to read image")
                continue
                
            h, w = img.shape[:2]
            aspect = w / h
            
            # Crop to matching aspect ratio first
            if aspect > target_aspect:
                # Image is too wide, crop width
                new_w = int(h * target_aspect)
                x_offset = (w - new_w) // 2
                img_cropped = img[:, x_offset:x_offset+new_w]
            elif aspect < target_aspect:
                # Image is too tall, crop height
                # For portraits, it's usually better to crop from the bottom (allow top headroom)
                new_h = int(w / target_aspect)
                y_offset = 0 # Crop from bottom instead of center
                img_cropped = img[y_offset:y_offset+new_h, :]
            else:
                img_cropped = img
                
            # Resize exactly to target dimensions
            img_resized = cv2.resize(img_cropped, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            # Save carefully to meet size limit (< 100KB)
            # Start with high quality and degrade if necessary
            quality = 95
            max_size = 100 * 1024 # 100 KB
            
            while quality > 10:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                result, encimg = cv2.imencode('.jpg', img_resized, encode_param)
                
                if result:
                    if len(encimg) < max_size:
                        # Found good quality
                        with open(out_filepath, 'wb') as f:
                            f.write(encimg)
                        print(f"[{id_str}] Saved at quality {quality} ({len(encimg)/1024:.1f} KB)")
                        break
                    else:
                        quality -= 5 # drop quality and retry
                else:
                    print(f"[{id_str}] Encoding failed")
                    break
                    
        except Exception as e:
            print(f"[{id_str}] Error: {e}")

if __name__ == "__main__":
    standardize_photos_v2()
