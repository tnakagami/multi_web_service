"""web_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('registration.urls',  namespace='registration')),
    path('sns/', include('sns.urls', namespace='sns')),
    path('blog/', include('blog.urls', namespace='blog')),
    path('storage/', include('storage.urls', namespace='storage')),
    path('chat/', include('chat.urls', namespace='chat')),
    path('deep_learning/', include('deep_learning.urls', namespace='deep_learning')),
    path('smarthome/', include('smarthome.urls', namespace='smarthome')),
]
