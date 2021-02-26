from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('create/tag', views.TagCreateView.as_view(), name='tag_create'),
    path('update/tag/<int:pk>', views.TagUpdateView.as_view(), name='tag_update'),
    path('create/post', views.PostCreateView.as_view(), name='post_create'),
    path('update/post/<int:pk>', views.PostUpdateView.as_view(), name='post_update'),
    path('detail/post/<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
    path('image/upload/', views.image_upload, name='image_upload'),
]
