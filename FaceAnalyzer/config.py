import cv2

TEMP_DIR = "temp_faces"
CASCADE_PATH = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
DEEPFACE_ACTIONS = ['age', 'gender', 'emotion', 'race']