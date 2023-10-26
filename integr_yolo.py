from ultralytics import YOLO
from PIL import Image
from pathlib import Path


path = Path('/path/to/model.pt')


model = YOLO(path)
# from PIL
im1 = Image.open("240292-Sepik.jpg")
model.predict(source=im1, save=True, conf=0.4)  # save plotted images in runs/detect/predict

# # для нескольких изображений
# results = model.predict(source=[im1, im2])