from django.urls import include, path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.RoomListView.as_view(), name='index'),
    path('room/create', views.RoomCreateView.as_view(), name='room_create'),
    path('room/update/<int:pk>', views.RoomUpdateView.as_view(), name='room_update'),
    path('room/delete/<int:pk>', views.RoomDeleteView.as_view(), name='room_delete'),
    path('room/<int:pk>', views.ChatRoomDetailView.as_view(), name='chat_room'),
]
