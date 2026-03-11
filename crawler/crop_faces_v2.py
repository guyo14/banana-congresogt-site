import os
import cv2
import numpy as np

def crop_and_standardize_faces():
    cwd = os.path.dirname(os.path.abspath(__file__))
    in_dir = os.path.join(cwd, "../public/congressmen-std")
    out_dir = os.path.join(cwd, "../public/face")
    
    os.makedirs(out_dir, exist_ok=True)
    
    if not os.path.exists(in_dir):
        print(f"Error: Images directory not found at {in_dir}")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    files = os.listdir(in_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"Extracting faces from {len(image_files)} images...")
    
    target_w, target_h = 300, 300
    
    for filename in image_files:
        filepath = os.path.join(in_dir, filename)
        id_str = os.path.splitext(filename)[0]
        out_filepath = os.path.join(out_dir, f"{id_str}.jpg")
        
        try:
            img = cv2.imread(filepath)
            if img is None:
                print(f"[{id_str}] Failed to read image")
                continue
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) == 0:
                print(f"[{id_str}] No face detected. Falling back to center crop.")
                h, w = img.shape[:2]
                min_dim = min(h, w)
                crop_size = int(min_dim * 0.8)
                x = (w - crop_size) // 2
                y = int((h - crop_size) * 0.3)
                face_img = img[y:y+crop_size, x:x+crop_size]
            else:
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                x, y, w, h = largest_face
                
                pad_w = int(w * 0.4)
                pad_h = int(h * 0.6)
                
                img_h, img_w = img.shape[:2]
                
                x1 = max(0, x - pad_w)
                y1 = max(0, y - int(pad_h * 0.8))
                x2 = min(img_w, x + w + pad_w)
                y2 = min(img_h, y + h + int(pad_h * 1.2))
                
                crop_w = x2 - x1
                crop_h = y2 - y1
                
                if crop_w > crop_h:
                    diff = crop_w - crop_h
                    y1 = max(0, y1 - diff//2)
                    y2 = min(img_h, y2 + (diff - diff//2))
                elif crop_h > crop_w:
                    diff = crop_h - crop_w
                    x1 = max(0, x1 - diff//2)
                    x2 = min(img_w, x2 + (diff - diff//2))
                
                face_img = img[y1:y2, x1:x2]
            
            img_resized = cv2.resize(face_img, (target_w, target_h), interpolation=cv2.INTER_AREA)
            
            # Save carefully to meet size limit (< 100KB)
            quality = 95
            max_size = 100 * 1024 # 100 KB
            
            while quality > 10:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
                result, encimg = cv2.imencode('.jpg', img_resized, encode_param)
                
                if result:
                    if len(encimg) < max_size:
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
             print(f"[{id_str}] Failed to process: {e}")

if __name__ == "__main__":
    crop_and_standardize_faces()
