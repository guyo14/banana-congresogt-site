import os
import cv2

def standardize_photos():
    cwd = os.path.dirname(os.path.abspath(__file__))
    images_dir = os.path.join(cwd, "../public/congressmen")

    if not os.path.exists(images_dir):
        print(f"Error: Images directory not found at {images_dir}")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    files = os.listdir(images_dir)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    print(f"Standardizing {len(image_files)} images...")
    
    for filename in image_files:
        filepath = os.path.join(images_dir, filename)
        
        id_str, ext = os.path.splitext(filename)
        out_filename = f"{id_str}.jpg"
        out_filepath = os.path.join(images_dir, out_filename)
        
        try:
            img = cv2.imread(filepath)
            if img is None:
                print(f"Failed to read image {filename}")
                continue
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            
            if len(faces) == 0:
                print(f"No face detected in {filename}. Falling back to center crop.")
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
            
            # Standardize ALL photos to exactly 300x300 and convert them to JPG
            face_img = cv2.resize(face_img, (300, 300), interpolation=cv2.INTER_AREA)

            # Do not overwrite if it is the same exact path and we are appending/editing in place.
            # But the requirement is to standardize everything. We will save it.
            cv2.imwrite(out_filepath, face_img)
            
            # If the original file wasn't a .jpg (e.g. .png, .jpeg), remove it.
            if out_filename != filename:
                os.remove(filepath)
                
            print(f"Standardized {filename} -> {out_filename}")
            
        except Exception as e:
             print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    standardize_photos()
