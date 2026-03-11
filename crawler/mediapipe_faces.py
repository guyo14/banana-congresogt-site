import os
import cv2
import mediapipe as mp
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

def process_with_mediapipe():
    cwd = os.path.dirname(os.path.abspath(__file__))
    in_dir = os.path.join(cwd, "../public/congressmen-std")
    out_dir = os.path.join(cwd, "../public/face")
    model_path = os.path.join(cwd, "blaze_face_short_range.tflite")
    
    # Download the required model if not exists
    if not os.path.exists(model_path):
        print("Downloading Face Detection Model...")
        urllib.request.urlretrieve(
            "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite",
            model_path
        )
    
    os.makedirs(out_dir, exist_ok=True)
    
    bad_ids = [
        '18', '31', '86', '117', '247', '772', '774', '785', '787', '796', 
        '864', '885', '887', '888', '893', '908', '915', '918', '919', '928', 
        '935', '953', '956', '959', '966', '969', '974'
    ]
    
    target_dim = 300
    
    print(f"Fixing {len(bad_ids)} faces using MediaPipe Tasks Vision...")

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceDetectorOptions(base_options=base_options)
    detector = vision.FaceDetector.create_from_options(options)
    
    for c_id in bad_ids:
        filepath = os.path.join(in_dir, f"{c_id}.jpg")
        out_filepath = os.path.join(out_dir, f"{c_id}.jpg")
        
        if not os.path.exists(filepath):
            print(f"[{c_id}] Missing in std folder: {filepath}")
            continue
            
        img = cv2.imread(filepath)
        if img is None:
            print(f"[{c_id}] Failed to read image")
            continue
            
        img_h, img_w = img.shape[:2]
        
        # Load image into MediaPipe format
        mp_image = mp.Image.create_from_file(filepath)
        detection_result = detector.detect(mp_image)
        
        if not detection_result.detections:
            print(f"[{c_id}] MediaPipe could not detect face! Falling back")
            side = 600
            x1 = (img_w - side) // 2
            x2 = x1 + side
            face_img = img[0:side, x1:x2]
        else:
            # First detection is usually highest conf
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
            y1 = cy - int(target_crop_size * 0.45)
            
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
                print(f"[{c_id}] MediaPipe Saved at Quality {quality} ({len(encimg)/1024:.1f} KB)")
                break

if __name__ == "__main__":
    process_with_mediapipe()
