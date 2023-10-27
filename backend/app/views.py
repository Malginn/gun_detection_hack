from json import loads
from random import randint
import os
from datetime import datetime

import requests
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from rest_framework.response import Response

import redis

from .tasks import make_nn_task


class NNView(APIView):
    def put(self, request):
        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                           port=settings.REDIS_PORT)
        try:
            file = request.data['file']
            current_time = datetime.now()
            filename = current_time.strftime('%Y%m%d%H%M%S%f') + os.path.splitext(file.name)[1]
            FileSystemStorage(location="/uploads").save(filename, file)
        except KeyError:
            raise Warning('Request has no resource file attached')

        redis_key = f"nn_{randint(1, 99999999)}"
        redis_instance.set(f"status_{redis_key}", 'starting')
        redis_instance.set(f"work_{redis_key}", str([]))
        make_nn_task.delay(redis_key, filename)

        return Response({"task_key": redis_key})


class TaskView(APIView):
    def get(self, request):

        task_key = request.GET.get('task_key')

        redis_instance = redis.StrictRedis(host=settings.REDIS_HOST,
                                           port=settings.REDIS_PORT)
        status = redis_instance.get(f"status_{task_key}")
        work = loads(redis_instance.get(f"work_{task_key}"))
        return Response({"status": status, "works": work})

class TaskView(APIView):
    def get(self,re):
        if requests.GET.get("task_key") == True:
            return  Response(status=200)

