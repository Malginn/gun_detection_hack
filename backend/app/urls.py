from django.urls import path, include

from .views import TaskView, NNView

urlpatterns = [
    path('task/', TaskView.as_view()),
    path('nn/', NNView.as_view()),
]