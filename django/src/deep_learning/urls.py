from django.urls import path
from . import views

app_name = 'deep_learning'

urlpatterns = [
    # top page
    path('', views.TopPageView.as_view(), name='index'),
    # what_docker
    path('what_docker/', views.WhatDockerView.as_view(), name='what_docker'),
    # docker_environment
    path('docker_environment/', views.DockerEnvironmentView.as_view(), name='docker_environment'),
    # use_docker
    path('use_docker/', views.UseDockerView.as_view(), name='use_docker'),
    # jupyter_notebook
    path('jupyter_notebook/', views.JupyterNotebookView.as_view(), name='jupyter_notebook'),
    # tutorial_mnist_dataset
    path('tutorial_mnist_dataset/', views.TutorialMnistDatasetView.as_view(), name='tutorial_mnist_dataset'),
    # handwriting_recognition
    path('handwriting_recognition/', views.HandwritingRecognitionView.as_view(), name='handwriting_recognition'),
]
