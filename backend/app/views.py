import ast
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
from django.http import FileResponse, HttpResponseNotFound, HttpResponse
from django.conf import settings
import os
from PIL import Image
import io
from pathlib import Path


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


class serve_media(APIView):
    def get(self, request):
        task_key = request.GET.get('task_key')
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        # Получите имя файла из Redis и преобразуйте его в список
        filename = redis_instance.get(f"work_{task_key}")
        if filename:
            filename_list = ast.literal_eval(filename.decode("utf-8"))

            if filename_list:
                # Извлеките первый путь к файлу из списка
                file_path = filename_list[0]

                # Откройте изображение
                image = Image.open(file_path)

                # Создайте буфер для сохранения изображения
                image_buffer = io.BytesIO()
                image.save(image_buffer, format='JPEG')

                # Перематываете буфер к началу
                image_buffer.seek(0)

                # Создайте HTTP-ответ и отправьте изображение
                response = HttpResponse(image_buffer.read(), content_type='image/jpeg')
                return response
            else:
                # Обработка ситуации, когда список пуст
                return HttpResponseNotFound("Список файлов пуст")
        else:
            # Обработка ситуации, когда имя файла не найдено в Redis
            return HttpResponseNotFound("Файл не найден в Redis")


class serve_video(APIView):
    def get(self, request):
        task_key = request.GET.get('task_key')
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

        # Получите имя видеофайла из Redis
        filename = redis_instance.get(f"work_{task_key}")
        print(filename)
        if filename:
            # Преобразуйте значение в строку
            filename_str = filename.decode("utf-8")

            # Если значение является списком, возьмите первый элемент
            filename_str = Path(filename_str[2:-2])

            # Определите MIME-тип для видео (например, video/mp4)
            content_type = "video/mp4"  # Замените на соответствующий тип для вашего видеоформата

            # Отправите видеофайл как HTTP-ответ
            response = HttpResponse(open(filename_str, 'rb'), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{filename_str}"'

            return response
        else:
            # Обработка ситуации, когда имя файла не найдено в Redis
            return HttpResponseNotFound("Файл не найден в Redis")