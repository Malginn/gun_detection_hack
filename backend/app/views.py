from random import randint
from datetime import datetime
import zipfile
import os

from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import redis
from setuptools.config._validate_pyproject import ValidationError

from .tasks import make_nn_task, archive_task


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





class RedisKeyListView(APIView):
    def get(self, request):
        # Подключение к Redis
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        # Получение всех ключей в Redis
        all_redis_keys = redis_instance.keys('*')

        # Преобразование байтовых ключей в строки
        all_redis_keys = [key.decode('utf-8') for key in all_redis_keys]

        return Response({"redis_keys": all_redis_keys})


class ArchveNN(APIView):
    def put(self, request):
        # Подключение к Redis
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                           port=settings.REDIS_PORT)
        try:
            file = request.data['file']
            current_time = datetime.now()
            filename = current_time.strftime('%Y%m%d%H%M%S%f') + os.path.splitext(file.name)[1]
            FileSystemStorage(location="./uploads").save(filename, file)
            file_paths = []
            with zipfile.ZipFile(f"./uploads/{filename}", 'r') as zip_ref:
                zip_ref.extractall("./uploads/")
                for file_name in zip_ref.namelist():
                    file_paths.append(os.path.join("./uploads/", file_name))
            print(file_paths)
        except KeyError:
            # Use ValidationError or BadRequest to handle the error and return an appropriate response.
            raise ValidationError('Request has no resource file attached', code='missing_file')

        redis_key = f"nn_{randint(1, 99999999)}"
        redis_instance.set(f"status_{redis_key}", 'starting')
        redis_instance.set(f"work_{redis_key}", str([]))

        archive_task.delay(redis_key, file_paths)

        status_value = redis_instance.get(f"status_{redis_key}")
        work_value = redis_instance.get(f"work_{redis_key}")

        return Response({
            "redis_key": redis_key,
            "status_value": status_value.decode("utf-8"),
            "work_value": work_value.decode("utf-8")
        })