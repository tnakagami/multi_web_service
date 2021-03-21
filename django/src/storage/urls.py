from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    # top page
    path('', views.StorageListView.as_view(), name='index'),
    # upload
    path('upload/', views.FileUploadView.as_view(), name='upload'),
    # update filename
    path('update/filename/<int:pk>', views.FilenameUpdateView.as_view(), name='update_filename'),
    # delete
    path('delete/<int:pk>', views.FileDeleteView.as_view(), name='delete'),
]
