import cv2
import numpy as np
import matplotlib.pyplot as plt

def preprocess_face(img, face_idx, face_cascade, show_visualizations=True):
    print(f"Preprocessing Face {face_idx}...")
    # Convert to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if show_visualizations:
        plt.figure(figsize=(5,5))
        plt.imshow(img_rgb)
        plt.title(f'Original Image (Face {face_idx})')
        plt.axis('off')
        plt.show(block=False)
        plt.pause(0.001)
        print(f"Displayed original image for Face {face_idx}")

    # Face detection (already done, but crop face for preprocessing)
    gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        print(f"No faces detected in preprocessing for Face {face_idx}.")
        return None, None

    # Take the first detected face (since this is a cropped face region)
    (x, y, w, h) = faces[0]
    face = img_rgb[y:y+h, x:x+w]

    if show_visualizations:
        plt.figure(figsize=(5,5))
        plt.imshow(face)
        plt.title(f"Detected & Cropped Face (Face {face_idx})")
        plt.axis('off')
        plt.show(block=False)
        plt.pause(0.001)
        print(f"Displayed cropped face for Face {face_idx}")

    # Apply median filter
    median_filtered = cv2.medianBlur(face, 5)

    # Apply bilateral filter
    bilateral_filtered = cv2.bilateralFilter(median_filtered, d=9, sigmaColor=75, sigmaSpace=75)

    if show_visualizations:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(face); axes[0].set_title(f"Before Denoising (Face {face_idx})"); axes[0].axis('off')
        axes[1].imshow(bilateral_filtered); axes[1].set_title(f"After Median + Bilateral (Face {face_idx})"); axes[1].axis('off')
        plt.show(block=False)
        plt.pause(0.001)
        print(f"Displayed denoising steps for Face {face_idx}")

    # Enhancement: CLAHE and sharpening
    lab = cv2.cvtColor(bilateral_filtered, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    lab_clahe = cv2.merge((cl, a, b))
    enhanced_clahe = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)

    kernel_sharpening = np.array([[0, -1, 0], [-1, 5,-1], [0, -1, 0]])
    sharpened = cv2.filter2D(enhanced_clahe, -1, kernel_sharpening)

    if show_visualizations:
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        axes[0].imshow(bilateral_filtered); axes[0].set_title(f"After Median + Bilateral (Face {face_idx})"); axes[0].axis('off')
        axes[1].imshow(enhanced_clahe); axes[1].set_title(f"After CLAHE (Face {face_idx})"); axes[1].axis('off')
        axes[2].imshow(sharpened); axes[2].set_title(f"After Sharpening (Face {face_idx})"); axes[2].axis('off')
        plt.show(block=False)
        plt.pause(0.001)
        print(f"Displayed CLAHE and sharpening for Face {face_idx}")

    # Histogram Equalization
    ycrcb = cv2.cvtColor(sharpened, cv2.COLOR_RGB2YCrCb)
    y, cr, cb = cv2.split(ycrcb)
    y_eq = cv2.equalizeHist(y)
    enhanced_final = cv2.cvtColor(cv2.merge([y_eq, cr, cb]), cv2.COLOR_YCrCb2RGB)

    if show_visualizations:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        axes[0].imshow(sharpened); axes[0].set_title(f"Before Equalization (Face {face_idx})"); axes[0].axis('off')
        axes[1].imshow(enhanced_final); axes[1].set_title(f"After Equalization (Face {face_idx})"); axes[1].axis('off')
        plt.show(block=False)
        plt.pause(0.001)
        print(f"Displayed histogram equalization for Face {face_idx}")

    # Resize to model's expected input
    resized = cv2.resize(enhanced_final, (227, 227))

    if show_visualizations:
        plt.figure(figsize=(5,5))
        plt.imshow(resized)
        plt.title(f"Preprocessed Face (227x227) (Face {face_idx})")
        plt.axis('off')
        plt.show(block=False)
        plt.pause(0.001)
        print(f"Displayed final preprocessed face for Face {face_idx}")

    # Return original face and enhanced face for DeepFace
    original_face = cv2.resize(face, (227, 227))
    return original_face, resized