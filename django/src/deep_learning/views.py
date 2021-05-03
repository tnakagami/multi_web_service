from django.views.generic import TemplateView

class TopPageView(TemplateView):
    template_name = 'deep_learning/index.html'

class WhatDockerView(TemplateView):
    template_name = 'deep_learning/what_docker.html'

class DockerEnvironmentView(TemplateView):
    template_name = 'deep_learning/docker_environment.html'

class UseDockerView(TemplateView):
    template_name = 'deep_learning/use_docker.html'

class JupyterNotebookView(TemplateView):
    template_name = 'deep_learning/jupyter_notebook.html'

class TutorialMnistDatasetView(TemplateView):
    template_name = 'deep_learning/tutorial_mnist_dataset.html'

class HandwritingRecognitionView(TemplateView):
    template_name = 'deep_learning/handwriting_recognition.html'
