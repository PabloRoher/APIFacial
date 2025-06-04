import sys
import json
import cv2
from ultralytics import YOLO
from PIL import Image
import numpy as np

EMOCIONES_LABELS = ['angry', 'happy', 'sad', 'surprised', 'neutral', 'fear', 'disgust']
EDAD_LABELS = ['0-5', '11-15', '16-20', '21-30', '31-40', '41-50', '51-60', '6-10', '60-']
GENERO_LABELS = ['mujer', 'hombre']

def run_model_on_crop(model, image_crop):
    # Convertir recorte de OpenCV a PIL, luego a formato compatible con YOLO
    image_pil = Image.fromarray(cv2.cvtColor(image_crop, cv2.COLOR_BGR2RGB))
    results = model(image_pil)
    if results[0].boxes:
        box = results[0].boxes[0]
        return {
            "class": int(box.cls[0]),
            "confidence": float(box.conf[0])
        }
    else:
        return None

def unify_results_multi_person(image_path):
    model_emocion = YOLO("emociones.pt")
    model_genero = YOLO("genero.pt")
    model_edad = YOLO("edad.pt")

    results = model_emocion(image_path)
    original_img = cv2.imread(image_path)

    detections = []
    for box in results[0].boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        face_crop = original_img[y1:y2, x1:x2]

        genero_pred = run_model_on_crop(model_genero, face_crop)
        edad_pred = run_model_on_crop(model_edad, face_crop)

        detections.append({
            "bbox": [float(x1), float(y1), float(x2), float(y2)],
            "emocion": EMOCIONES_LABELS[int(box.cls[0])],
            "emocion_conf": float(box.conf[0]),
            "genero": GENERO_LABELS[genero_pred["class"]] if genero_pred else None,
            "genero_conf": genero_pred["confidence"] if genero_pred else None,
            "edad": EDAD_LABELS[edad_pred["class"]] if edad_pred else None,
            "edad_conf": edad_pred["confidence"] if edad_pred else None
        })

    return detections

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python predict.py <path_to_image>")
        sys.exit(1)

    img_path = sys.argv[1]
    unified = unify_results_multi_person(img_path)
    print(json.dumps(unified))