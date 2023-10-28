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

    work_list.append(f"./yolo/{redis_key}/{file}")
    redis_instance.set(f"work_{redis_key}", str(work_list))
    redis_instance.set(f"status_{redis_key}", 'done')

    src_path = f"./yolo/{redis_key}/"
    link_path = f"../Frontend/yolo/{redis_key}/"  # Замените на нужное вам имя
    os.symlink(src_path, link_path)

@shared_task
def archive_task(redis_key, array_path):
    path = Path('./app/valid_big_final.pt')
    print(redis_key)
    redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                       port=settings.REDIS_PORT)

    redis_instance.set(f"status_{redis_key}", 'run')
    array_photo = []
    for i in range(len(array_path)):
        img = Image.open(array_path[i])
        array_photo.append(img)

    model = YOLO(path)
    model.predict(source=array_photo, save=True, conf=0.3,project='yolo', name=redis_key)
    work_list = loads(redis_instance.get(f"work_{redis_key}"))

    for item in range(len(array_photo)):
        new_item = f"./yolo/{redis_key}/{item}.jpg"
        work_list.append(new_item)

    redis_instance.set(f"work_{redis_key}", str(work_list))
    redis_instance.set(f"status_{redis_key}", 'done')
