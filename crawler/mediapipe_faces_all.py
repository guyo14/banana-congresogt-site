import os
import cv2
import mediapipe as mp
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

def process_all_with_mediapipe():
    cwd = os.path.dirname(os.path.abspath(__file__))
    in_dir = os.path.join(cwd, "../public/congressmen-std")
    out_dir = os.path.join(cwd, "../public/face")
    model_path = os.path.join(cwd, "blaze_face_short_range.tflite")
    
    # Download the required MediaPipe model if not exists
    if not os.path.exists(model_path):
        print("Downloading Face Detection Model...")
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite",
            model_path
        )
    
    os.makedirs(out_dir, exist_ok=True)
    
    # Get all standardized images
    image_files = [f for f in os.listdir(in_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    target_dim = 300
    
    print(f"Applying MediaPipe crop to all {len(image_files)} images...")

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceDetectorOptions(base_options=base_options)
    detector = vision.FaceDetector.create_from_options(options)
    
    for filename in image_files:
        filepath = os.path.join(in_dir, filename)
        id_str = os.path.splitext(filename)[0]
        out_filepath = os.path.join(out_dir, f"{id_str}.jpg")
            
        img = cv2.imread(filepath)
        if img is None:
            print(f"[{id_str}] Failed to read image")
            continue
            
        img_h, img_w = img.shape[:2]
        
        # Load image into MediaPipe format
        mp_image = mp.Image.create_from_file(filepath)
        detection_result = detector.detect(mp_image)
        
        if not detection_result.detections:
            print(f"[{id_str}] MediaPipe could not detect face! Falling back")
            side = 600
            x1 = (img_w - side) // 2
            x2 = x1 + side
            face_img = img[0:side, x1:x2]
        else:
            # The exact logic used for 785
            detection = detection_result.detections[0]
            bbox = detection.bounding_box
            
            xmin = bbox.origin_x
            ymin = bbox.origin_y
            w = bbox.width
            h = bbox.height
            
            target_crop_size = int(w * 2.5) 
            target_crop_size = min(target_crop_size, img_w, img_h)
            
            cx = xmin + w // 2
            cy = ymin + h // 2
            
            x1 = cx - target_crop_size // 2
            y1 = cy - int(target_crop_size * 0.45) # Keep the head properly shifted down slightly for shoulders
            
            x2 = x1 + target_crop_size
            y2 = y1 + target_crop_size
            
            if x1 < 0:
                x2 -= x1; x1 = 0
            if y1 < 0:
                y2 -= y1; y1 = 0
            if x2 > img_w:
                x1 -= (x2 - img_w); x2 = img_w
            if y2 > img_h:
                y1 -= (y2 - img_h); y2 = img_h
                
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(img_w, x2), min(img_h, y2)
            
            face_img = img[y1:y2, x1:x2]
            
            dh, dw = face_img.shape[:2]
            side_min = min(dh, dw)
            face_img = face_img[0:side_min, 0:side_min]
            
        img_resized = cv2.resize(face_img, (target_dim, target_dim), interpolation=cv2.INTER_AREA)
        
        max_size = 100 * 1024
        for quality in range(95, 10, -5):
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            result, encimg = cv2.imencode('.jpg', img_resized, encode_param)
            if result and len(encimg) < max_size:
                with open(out_filepath, 'wb') as f:
                    f.write(encimg)
                print(f"[{id_str}] Saved at Quality {quality} ({len(encimg)/1024:.1f} KB)")
                break

if __name__ == "__main__":
    process_all_with_mediapipe()
