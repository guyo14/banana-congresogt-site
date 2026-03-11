import os
import cv2

def crop_faces_v3():
    cwd = os.path.dirname(os.path.abspath(__file__))
    in_dir = os.path.join(cwd, "../public/congressmen-std")
    out_dir = os.path.join(cwd, "../public/face")
    
    os.makedirs(out_dir, exist_ok=True)
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    face_cascade_alt = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')

    image_files = [f for f in os.listdir(in_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"Extracting robust faces from {len(image_files)} images...")
    
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
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect face
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
            if len(faces) == 0:
                faces = face_cascade_alt.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40))
                
            if len(faces) > 0:
                largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
                fx, fy, fw, fh = largest_face
                
                # Headshot framing
                side = int(fw * 2.2) # crop width around the face
                side = min(side, img_w, img_h)
                
                cx = fx + fw // 2
                cy = fy + fh // 2
                
                # Center face about 45% from top of crop
                x1 = cx - side // 2
                y1 = cy - int(side * 0.45)
            else:
                # Fallback: Top center crop for standard 600x800 image
                side = 460
                x1 = (img_w - side) // 2
                y1 = 80
                
            x2 = x1 + side
            y2 = y1 + side
            
            # Shift bounds to stay inside picture keeping EXACT same size
            if x1 < 0:
                x2 -= x1
                x1 = 0
            if y1 < 0:
                y2 -= y1
                y1 = 0
            if x2 > img_w:
                x1 -= (x2 - img_w)
                x2 = img_w
            if y2 > img_h:
                y1 -= (y2 - img_h)
                y2 = img_h
                
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(img_w, x2)
            y2 = min(img_h, y2)
            
            face_img = img[y1:y2, x1:x2]
            
            # Ensure strictly square crop 1:1 before resizing (just in case bounds shifting hit a corner)
            fh, fw = face_img.shape[:2]
            sd = min(fh, fw)
            face_img = face_img[0:sd, 0:sd]
            
            img_resized = cv2.resize(face_img, (target_dim, target_dim), interpolation=cv2.INTER_AREA)
            
            # Compressing under 100KB
            quality = 95
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
    crop_faces_v3()
