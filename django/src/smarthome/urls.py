from django.urls import path
from . import views

app_name = 'smarthome'

urlpatterns = [
    # top page
    path('', views.IndexView.as_view(), name='index'),
    # create access token
    path('create/access_token', views.AccessTokenCreateView.as_view(), name='create_access_token'),
    # get access url
    path('get/url/<str:method>/<str:token>', views.get_access_url, name='get_access_url'),
    # open entrance door
    path('open/entrance/<str:token>', views.open_entrance, name='open_entrance')
]
