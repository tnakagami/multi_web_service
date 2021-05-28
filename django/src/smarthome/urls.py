from django.urls import path
from . import views

app_name = 'smarthome'

urlpatterns = [
    # top page
    path('', views.IndexView.as_view(), name='index'),
    # create access token
    path('create/access_token', views.AccessTokenCreateView.as_view(), name='create_access_token'),
    # open entrance door
    path('open/entrance/<str:token>', views.open_entrance, name='open_entrance')
]
