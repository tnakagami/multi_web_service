from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # top page
    path('', views.PostListView.as_view(), name='index'),
    # own post
    path('own/post/<int:pk>', views.OwnPostListView.as_view(), name='own_post'),
    # own tag
    path('own/tag/<int:pk>', views.OwnTagListView.as_view(), name='own_tag'),
    # create or update tag
    path('create/tag', views.TagCreateView.as_view(), name='tag_create'),
    path('update/tag/<int:pk>', views.TagUpdateView.as_view(), name='tag_update'),
    # create or update post
    path('create/post', views.PostCreateView.as_view(), name='post_create'),
    path('update/post/<int:pk>', views.PostUpdateView.as_view(), name='post_update'),
    # detail post
    path('detail/post/<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
    path('image/upload/', views.image_upload, name='image_upload'),
]
