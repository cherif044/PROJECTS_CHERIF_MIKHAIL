import cv2
import time
from face_preprocessing import preprocess_face
from face_analysis import get_pred_label, draw_label
from PIL import Image
import os
from config import TEMP_DIR, DEEPFACE_ACTIONS
from deepface import DeepFace

def open_webcam():
    for index in [0, 1, 2]:
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Webcam opened successfully on index {index}.")
            return cap, index
    print("Error: Could not open webcam on indices 0, 1, or 2. Check permissions or device.")
    return None, None

def is_same_face(face1, face2, threshold=50):
    x1, y1, w1, h1 = face1
    x2, y2, w2, h2 = face2
    return (abs(x1 - x2) < threshold and
            abs(y1 - y2) < threshold and
            abs(w1 - w2) < threshold and
            abs(h1 - h2) < threshold)

def process_webcam(cap, face_cascade):
    stored_faces = []
    capture_triggered = False
    error_message = ""
    last_capture_time = time.time()
    last_predictions = {}

    print("Starting webcam... Press 's' to capture detected faces manually, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4)

        current_time = time.time()
        auto_capture = (current_time - last_capture_time >= 15.0) and len(faces) > 0

        if len(faces) > 0:
            frame_predictions = {}
            for i, (x, y, w, h) in enumerate(faces):
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(frame, f"Face {i+1}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX,
                            0.8, (0, 255, 0), 2, cv2.LINE_AA)

                face_key = f"{x}_{y}_{w}_{h}"
                matched_key = None
                for prev_key in last_predictions:
                    prev_x, prev_y, prev_w, prev_h = map(int, prev_key.split('_'))
                    if is_same_face((x, y, w, h), (prev_x, prev_y, prev_w, prev_h)):
                        matched_key = prev_key
                        break

                if matched_key and not auto_capture:
                    label_original, label_enhanced = last_predictions[matched_key]
                else:
                    label_original = "Processing..."
                    label_enhanced = "Processing..."
                    if auto_capture:
                        face_rgb = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
                        original_face, enhanced_face = preprocess_face(face_rgb, i+1, face_cascade, show_visualizations=False)
                        if original_face is None or enhanced_face is None:
                            label_original = "Processing Error"
                            label_enhanced = "Processing Error"
                        else:
                            print(f"Storing face {i+1} in RGB format for final plot.")
                            original_path = os.path.join(TEMP_DIR, f"original_face_{i}.jpg")
                            enhanced_path = os.path.join(TEMP_DIR, f"enhanced_face_{i}.jpg")
                            Image.fromarray(original_face).save(original_path)
                            Image.fromarray(enhanced_face).save(enhanced_path)

                            try:
                                result_original = DeepFace.analyze(img_path=original_path, actions=DEEPFACE_ACTIONS, enforce_detection=False)
                                result_enhanced = DeepFace.analyze(img_path=enhanced_path, actions=DEEPFACE_ACTIONS, enforce_detection=False)
                                label_original = get_pred_label(result_original)
                                label_enhanced = get_pred_label(result_enhanced)
                                stored_faces.append((original_face, enhanced_face, result_original, result_enhanced))
                            except Exception as e:
                                print(f"DeepFace error for Face {i+1}: {e}")
                                label_original = "Error in Prediction"
                                label_enhanced = "Error in Prediction"
                            finally:
                                try:
                                    os.remove(original_path)
                                    os.remove(enhanced_path)
                                except OSError as e:
                                    print(f"Error deleting temporary file: {e}")

                frame_predictions[face_key] = (label_original, label_enhanced)

                y_offset = y - 100 if y - 100 > 0 else 20
                for j, line in enumerate(label_original.split('\n')):
                    cv2.putText(frame, f"O: {line}", (x, y_offset + j*20), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (255, 255, 0), 2, cv2.LINE_AA)
                for j, line in enumerate(label_enhanced.split('\n')):
                    cv2.putText(frame, f"E: {line}", (x, y_offset + (j+2)*20), cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (255, 255, 0), 2, cv2.LINE_AA)

            if auto_capture:
                last_predictions = frame_predictions
                last_capture_time = current_time
                print("Processed and captured faces after 15 seconds.")

            error_message = ""
        else:
            error_message = "No Face Detected"
            cv2.putText(frame, error_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1.0, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow('Face Tracking - Press s to Capture, q to Quit', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            if len(faces) > 0:
                capture_triggered = True
                for i, (x, y, w, h) in enumerate(faces):
                    face_rgb = cv2.cvtColor(frame[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
                    original_face, enhanced_face = preprocess_face(face_rgb, i+1, face_cascade, show_visualizations=False)
                    if original_face is None or enhanced_face is None:
                        continue

                    print(f"Storing manually captured face {i+1} in RGB format.")
                    original_path = os.path.join(TEMP_DIR, f"original_face_{i}.jpg")
                    enhanced_path = os.path.join(TEMP_DIR, f"enhanced_face_{i}.jpg")
                    Image.fromarray(original_face).save(original_path)
                    Image.fromarray(enhanced_face).save(enhanced_path)

                    try:
                        result_original = DeepFace.analyze(img_path=original_path, actions=DEEPFACE_ACTIONS, enforce_detection=False)
                        result_enhanced = DeepFace.analyze(img_path=enhanced_path, actions=DEEPFACE_ACTIONS, enforce_detection=False)
                        label_original = get_pred_label(result_original)
                        label_enhanced = get_pred_label(result_enhanced)
                        face_key = f"{x}_{y}_{w}_{h}"
                        last_predictions[face_key] = (label_original, label_enhanced)
                        stored_faces.append((original_face, enhanced_face, result_original, result_enhanced))
                    except Exception as e:
                        print(f"DeepFace error for Face {i+1}: {e}")
                    finally:
                        try:
                            os.remove(original_path)
                            os.remove(enhanced_path)
                        except OSError as e:
                            print(f"Error deleting temporary file: {e}")
                print("Manual capture triggered.")
            else:
                error_message = "Error: No face detected to capture"
                print(error_message)
                cv2.putText(frame, error_message, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1.0, (0, 0, 255), 2, cv2.LINE_AA)
                cv2.imshow('Face Tracking - Press s to Capture, q to Quit', frame)
                cv2.waitKey(1000)

    return stored_faces