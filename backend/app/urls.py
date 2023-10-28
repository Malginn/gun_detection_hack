from django.urls import path, include

from .views import TaskView, NNView, RedisKeyListView, ArchveNN, serve_media, serve_video

urlpatterns = [
    path('task/', TaskView.as_view()),
    path('nn/', NNView.as_view()),
    path('archive/', ArchveNN.as_view()),
    path('redis/', RedisKeyListView.as_view()),
    path('media/', serve_media.as_view(), name='serve_media'),
    path('video/', serve_video.as_view(), name='serve_video'),
]