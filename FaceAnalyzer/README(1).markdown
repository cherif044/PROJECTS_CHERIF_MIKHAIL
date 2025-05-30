# Face Detection and Analysis

This project detects faces in images or webcam streams, preprocesses them, and analyzes attributes such as age, gender, emotion, and race using the DeepFace library. It supports two modes: analyzing an uploaded image or real-time webcam face tracking.

## Features

- **Face Detection**: Uses OpenCV's Haar Cascade for robust face detection.
- **Preprocessing**: Applies filtering, CLAHE, sharpening, and histogram equalization to enhance faces.
- **Analysis**: Leverages DeepFace to predict age, gender, emotion, and race.
- **Visualization**: Displays results using Matplotlib for images and OpenCV for webcam streams.
- **Modes**:
  - **Image Upload**: Analyze faces in a selected image.
  - **Webcam**: Real-time face tracking with manual capture (press 's') or auto-capture every 15 seconds.

## Project Structure

```
face_detection_project/
├── main.py                # Program entry point
├── face_preprocessing.py  # Face preprocessing functions
├── face_analysis.py       # DeepFace analysis logic
├── webcam_utils.py        # Webcam handling utilities
├── image_utils.py         # Image loading and handling
├── visualization.py       # Matplotlib visualization functions
├── config.py             # Configuration settings
└── README.md             # Project documentation
```

## Requirements

- **Python**: 3.7 or higher
- **Dependencies**: 
  - `opencv-python`
  - `deepface`
  - `matplotlib`
  - `pillow`
- **Hardware**: Webcam (required for webcam mode)
- **OpenCV Haar Cascade**: Ensure `haarcascade_frontalface_default.xml` is accessible.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/face_detection_project.git
   ```

2. Navigate to the project directory:
   ```bash
   cd face_detection_project
   ```

3. Install the required dependencies:
   ```bash
   pip install opencv-python deepface matplotlib pillow
   ```

4. Verify that OpenCV's `haarcascade_frontalface_default.xml` is available in your OpenCV installation.

## How to Run

1. Navigate to the project directory:
   ```bash
   cd face_detection_project
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Choose a mode:
   - **Option 1**: Webcam mode (press 's' to capture a frame, 'q' to quit).
   - **Option 2**: Image upload mode (select an image via file picker or Colab widget).

4. View results:
   - **Image Upload Mode**: Displays preprocessing steps and predictions.
   - **Webcam Mode**: Shows real-time face tracking with final results after quitting.

## Testing with a Photo

1. Prepare a clear, well-lit image with visible faces (e.g., `test.jpg`).
2. Run `python main.py` and select option 2.
3. Select the image via the file picker.
4. View results, including the original and enhanced face predictions.

**Tip**: Use high-quality, well-lit images for optimal results.

## Notes

- Temporary files are saved in the `temp_faces` directory and deleted after execution.
- Webcam mode requires an accessible webcam.
- Google Colab supports image upload mode but not webcam mode.

## Troubleshooting

- **No faces detected**: Ensure the image is clear or adjust detection parameters in `config.py`.
- **Webcam errors**: Verify webcam permissions or try different indices in `webcam_utils.py`.
- **Matplotlib issues**: Ensure compatibility with the TkAgg backend.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.