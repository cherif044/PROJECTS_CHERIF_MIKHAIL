import cv2
from deepface import DeepFace
from PIL import Image
import os
from config import TEMP_DIR, DEEPFACE_ACTIONS
from face_preprocessing import preprocess_face

def get_pred_label(result):
    if not result or not result[0]:
        return "No prediction"
    gender_probs = result[0]['gender']
    predicted_gender = max(gender_probs, key=gender_probs.get)
    predicted_age = result[0]['age']
    predicted_emotion = result[0]['dominant_emotion']
    predicted_race = result[0]['dominant_race']
    return f"{predicted_gender}, {predicted_age:.0f} yrs\n{predicted_emotion}, {predicted_race}"

def draw_label(image, label):
    # Ensure input image is in RGB format
    if image.shape[2] == 3:  # Check if image has 3 channels
        img_rgb = image.copy()  # Assume RGB, make a copy to avoid modifying original
    else:
        print("Warning: Input image to draw_label has unexpected channels.")
        return image

    # Convert to BGR for OpenCV text drawing
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    for i, line in enumerate(label.split('\n')):
        cv2.putText(img_bgr, line, (10, 30 + i*30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.8, (255, 255, 0), 2, cv2.LINE_AA)
    # Convert back to RGB for matplotlib display
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)

def analyze_faces(img, face_cascade, show_visualizations=True):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        print("No faces detected.")
        return []

    results = []
    for i, (x, y, w, h) in enumerate(faces):
        face = img_rgb[y:y+h, x:x+w]
        original_face, enhanced_face = preprocess_face(face, i+1, face_cascade, show_visualizations)
        if original_face is None or enhanced_face is None:
            continue

        original_path = os.path.join(TEMP_DIR, f"original_face_{i}.jpg")
        enhanced_path = os.path.join(TEMP_DIR, f"enhanced_face_{i}.jpg")
        Image.fromarray(original_face).save(original_path)
        Image.fromarray(enhanced_face).save(enhanced_path)

        try:
            result_original = DeepFace.analyze(img_path=original_path, actions=DEEPFACE_ACTIONS, enforce_detection=False)
            result_enhanced = DeepFace.analyze(img_path=enhanced_path, actions=DEEPFACE_ACTIONS, enforce_detection=False)
            results.append((original_face, enhanced_face, result_original, result_enhanced))
        except Exception as e:
            print(f"DeepFace error for Face {i+1}: {e}")
        finally:
            try:
                os.remove(original_path)
                os.remove(enhanced_path)
            except OSError as e:
                print(f"Error deleting temporary file: {e}")

    return results