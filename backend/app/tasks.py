from json import loads
from django.conf import settings
from celery import shared_task
import redis

from ultralytics import YOLO
from PIL import Image
from pathlib import Path




@shared_task()
def make_nn_task(redis_key, file):
    redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                       port=settings.REDIS_PORT)

    redis_instance.set(f"status_{redis_key}", 'run')
    path = Path('yolov8l_0.95mAP_13epochs')
    #начинается выполнение работы нейронки
    model = YOLO(path)
    im1 = Image.open(file)
    results = model.predict(source=im1, save=True, conf=0.4)  # save plotted images in runs/detect/predict


    #заканчивается выполнение работы нейронки



    work_list = loads(redis_instance.get(f"work_{redis_key}"))
    work_list.append({'time': 1, 'v': 45})
    redis_instance.set(f"work_{redis_key}", str(work_list))
    redis_instance.set(f"status_{redis_key}", 'done')
