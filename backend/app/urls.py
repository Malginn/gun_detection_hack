from django.urls import path, include

from .views import TaskView, NNView, RedisKeyListView

urlpatterns = [
    path('task/', TaskView.as_view()),
    path('nn/', NNView.as_view()),
    path('redis/', RedisKeyListView.as_view()),
]