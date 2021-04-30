from django.urls import path
from django.views.generic import TemplateView

app_name = 'deep_learning'

urlpatterns = [
    # top page
    path('', TemplateView.as_view(template_name='{}/index.html'.format(app_name)), name='index'),
    # what_docker
    path('what_docker/', TemplateView.as_view(template_name='{}/what_docker.html'.format(app_name)), name='what_docker'),
    # docker_environment
    path('docker_environment/', TemplateView.as_view(template_name='{}/docker_environment.html'.format(app_name)), name='docker_environment'),
    # use_docker
    path('use_docker/', TemplateView.as_view(template_name='{}/use_docker.html'.format(app_name)), name='use_docker'),
    # jupyter_notebook
    path('jupyter_notebook/', TemplateView.as_view(template_name='{}/jupyter_notebook.html'.format(app_name)), name='jupyter_notebook'),
    # tutorial_mnist_dataset
    path('tutorial_mnist_dataset/', TemplateView.as_view(template_name='{}/tutorial_mnist_dataset.html'.format(app_name)), name='tutorial_mnist_dataset'),
    # handwriting_recognition
    path('handwriting_recognition/', TemplateView.as_view(template_name='{}/handwriting_recognition.html'.format(app_name)), name='handwriting_recognition'),
]
