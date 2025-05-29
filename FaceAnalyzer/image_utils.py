import os
import shutil
import cv2
import tkinter as tk
from tkinter import filedialog
from config import TEMP_DIR

def setup_temp_dir():
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

def cleanup_temp_dir():
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

def upload_image():
    try:
        from google.colab import files
        uploaded = files.upload()
        img_path = list(uploaded.keys())[0]
        img = cv2.imread(img_path)
    except:
        root = tk.Tk()
        root.withdraw()
        img_path = filedialog.askopenfilename(title="Select an image")
        img = cv2.imread(img_path)
    return img