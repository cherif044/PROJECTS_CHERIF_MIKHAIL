import os
import shutil
import cv2
from config import TEMP_DIR, CASCADE_PATH
from image_utils import setup_temp_dir, cleanup_temp_dir, upload_image
from webcam_utils import open_webcam, process_webcam
from visualization import display_final_results
from face_analysis import analyze_faces

def main():
    # Setup temporary directory
    setup_temp_dir()

    # User choice: webcam or upload
    print("Choose input method:")
    print("1. Webcam (track faces, press 's' to capture)")
    print("2. Upload a single picture")
    choice = input("Enter 1 or 2: ")

    # Load Haar Cascade for face detection
    face_cascade = cv2.CascadeClassifier(CASCADE_PATH)
    if face_cascade.empty():
        print("Error: Could not load Haar Cascade classifier.")
        cleanup_temp_dir()
        exit()

    if choice == "2":
        # Upload mode
        img = upload_image()
        if img is None:
            print("Error: Could not load the image.")
            cleanup_temp_dir()
            exit()

        # Process and analyze faces
        results = analyze_faces(img, face_cascade, show_visualizations=True)
        if results:
            display_final_results(results)
        else:
            print("No valid faces processed.")
        
        cleanup_temp_dir()
        exit()

    # Webcam mode
    cap, webcam_index = open_webcam()
    results = process_webcam(cap, face_cascade)
    
    # Release webcam and display results
    cap.release()
    cv2.destroyAllWindows()
    if results:
        display_final_results(results)
    else:
        print("No faces captured for processing.")
    
    cleanup_temp_dir()

if __name__ == "__main__":
    main()