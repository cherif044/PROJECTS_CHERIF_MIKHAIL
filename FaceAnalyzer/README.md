Face Detection and Analysis

This project detects faces in images or webcam streams, preprocesses them, and analyzes attributes (age, gender, emotion, race) using DeepFace. It supports two modes: analyzing an uploaded image or real-time webcam face tracking.

Features

Detects faces using OpenCV's Haar Cascade.
Preprocesses faces with filtering, CLAHE, sharpening, and histogram equalization.
Analyzes faces with DeepFace for age, gender, emotion, and race.
Displays results with Matplotlib (images) and OpenCV (webcam).
Modes: Image upload or webcam (manual capture with 's', auto-capture every 15s).

Project Structure:
face_detection_project/
├── main.py                # Program entry point
├── face_preprocessing.py  # Face preprocessing
├── face_analysis.py       # DeepFace analysis
├── webcam_utils.py        # Webcam handling
├── image_utils.py         # Image loading
├── visualization.py       # Matplotlib visualizations
├── config.py             # Configuration
└── README.md             # Documentation

Requirements

Python 3.7+
Dependencies: opencv-python, deepface, matplotlib, pillow
Webcam (for webcam mode)

Installation

Install dependencies:pip install opencv-python deepface matplotlib pillow


Ensure OpenCV's haarcascade_frontalface_default.xml is accessible.

How to Run

Navigate to the project directory:cd face_detection_project


Run the application:python main.py


Choose mode:
1: Webcam mode (press 's' to capture, 'q' to quit).
2: Upload mode (select an image via file picker or Colab widget).


View results:
Upload mode: Preprocessing steps and predictions displayed.
Webcam mode: Real-time face tracking with final results after quitting.



Testing with a Photo

Prepare a clear image with visible faces (e.g., test.jpg).
Run python main.py and select option 2.
Choose the image via the file picker.
Results show original and enhanced face predictions.Tip: Use well-lit, high-quality images for best results.

Notes

Temporary files are stored in temp_faces and deleted after execution.
Webcam mode requires an accessible webcam.
Colab supports upload mode but not webcam mode.

Troubleshooting

No faces detected: Ensure image quality or adjust detection parameters in config.py.
Webcam errors: Check permissions or try different indices in webcam_utils.py.
Matplotlib issues: Verify TkAgg backend compatibility.

License
MIT License. See LICENSE for details.
