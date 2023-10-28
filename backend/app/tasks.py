import os
from json import loads
from django.conf import settings
from celery import shared_task
import redis
from ultralytics import YOLO
from PIL import Image
from pathlib import Path



@shared_task
def make_nn_task(redis_key, file):
    path = Path('./app/modelnn.pt')
    print(redis_key)
    redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                       port=settings.REDIS_PORT)

    redis_instance.set(f"status_{redis_key}", 'run')

    model = YOLO(path)
    im1 = Path('./uploads/' + file)
    model.predict(source=im1, save=True, conf=0.4,project='yolo', name=redis_key)
    work_list = loads(redis_instance.get(f"work_{redis_key}"))

    work_list.append(f"./yolo/{redis_key}/")
    redis_instance.set(f"work_{redis_key}", work_list[0])
    redis_instance.set(f"status_{redis_key}", 'done')

@shared_task
def archive_task(redis_key, array_path):
    path = Path('./app/best_nano88.pt')
    print(redis_key)
    redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                       port=settings.REDIS_PORT)

    redis_instance.set(f"status_{redis_key}", 'run')
    arra_photo = []
    for i in range(len(array_path)):
        img = Image.open(array_path[i])
        arra_photo.append(img)

    model = YOLO(path)
    model.predict(source=arra_photo, save=True, conf=0.3,project='yolo', name=redis_key)
    work_list = loads(redis_instance.get(f"work_{redis_key}"))

    work_list.append(f"./yolo/{redis_key}/")
    redis_instance.set(f"work_{redis_key}", work_list[0])
    redis_instance.set(f"status_{redis_key}", 'done')
