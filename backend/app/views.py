from json import loads
from random import randint
import os
from datetime import datetime

import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
import os
from json import loads
from django.conf import settings
from celery import shared_task
import redis
from ultralytics import YOLO
from PIL import Image
from pathlib import Path


import redis
from setuptools.config._validate_pyproject import ValidationError



class NNView(APIView):
    def put(self, request):
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                           port=settings.REDIS_PORT)
        try:
            file = request.data['file']
            current_time = datetime.now()
            filename = current_time.strftime('%Y%m%d%H%M%S%f') + os.path.splitext(file.name)[1]
            FileSystemStorage(location="./uploads").save(filename, file)
        except KeyError:
            # Use ValidationError or BadRequest to handle the error and return an appropriate response.
            raise ValidationError('Request has no resource file attached', code='missing_file')

        redis_key = f"nn_{randint(1, 99999999)}"
        redis_instance.set(f"status_{redis_key}", 'starting')
        redis_instance.set(f"work_{redis_key}", str([]))
        print('./app/uploads/' + filename)
        print(filename, file)
        make_nn_task.delay(redis_key, filename)
        status_value = redis_instance.get(f"status_{redis_key}")
        work_value = redis_instance.get(f"work_{redis_key}")

        return Response({
            "redis_key": redis_key,
            "status_value": status_value.decode("utf-8"),
            "work_value": work_value.decode("utf-8")
        })  # Return a proper HTTP 200 response


class TaskView(APIView):
    def get(self, request):
        task_key = request.GET.get('task_key')
        print(task_key)
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                           port=settings.REDIS_PORT)

        status_value = redis_instance.get(f"status_{task_key}")
        work_value = redis_instance.get(f"work_{task_key}")
        return Response({"status": status_value.decode("utf-8"), "work": work_value.decode("utf-8")})



@shared_task
def make_nn_task(redis_key, file):
    path = Path('./app/modelnn.pt')
    print(redis_key)
    redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                       port=settings.REDIS_PORT)

    redis_instance.set(f"status_{redis_key}", 'run')

    model = YOLO(path)
    im1 = Image.open('./uploads/' + file)

    model.predict(source=im1, save=True, conf=0.4,project='yolo', name=redis_key)
    work_list = loads(redis_instance.get(f"work_{redis_key}"))

    work_list.append(f"./yolo/{redis_key}/")
    redis_instance.set(f"work_{redis_key}", work_list[0])
    redis_instance.set(f"status_{redis_key}", 'done')


class RedisKeyListView(APIView):
    def get(self, request):
        # Подключение к Redis
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        # Получение всех ключей в Redis
        all_redis_keys = redis_instance.keys('*')

        # Преобразование байтовых ключей в строки
        all_redis_keys = [key.decode('utf-8') for key in all_redis_keys]

        return Response({"redis_keys": all_redis_keys})