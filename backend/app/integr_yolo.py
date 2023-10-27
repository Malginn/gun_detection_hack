from ultralytics import YOLO
from PIL import Image
from pathlib import Path


path = Path('yolov8l_0.95mAP_13epochs')


model = YOLO(path)
# from PIL
im1 = Image.open("240292-Sepik.jpg")
results = model.predict(source=im1, save=True)  # save plotted images in runs/detect/predict

# # для нескольких изображений
# results = model.predict(source=[im1, im2])