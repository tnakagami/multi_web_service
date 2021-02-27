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
    # create, update or delete tag
    path('tag/create', views.TagCreateView.as_view(), name='tag_create'),
    path('tag/update/<int:pk>', views.TagUpdateView.as_view(), name='tag_update'),
    path('tag/delete/<int:pk>', views.TagDeleteView.as_view(), name='tag_delete'),
    # create, update or delete post
    path('post/create', views.PostCreateView.as_view(), name='post_create'),
    path('post/update/<int:pk>', views.PostUpdateView.as_view(), name='post_update'),
    path('post/delete/<int:pk>', views.PostDeleteView.as_view(), name='post_delete'),
    # detail post
    path('post/detail/<int:pk>', views.PostDetailView.as_view(), name='post_detail'),
    # create comment
    path('comment/create/<int:pk>', views.CommentCreateView.as_view(), name='comment_create'),
    # reply
    path('reply/create/<int:pk>', views.ReplyCreateView.as_view(), name='reply_create'),
    path('image/upload/', views.image_upload, name='image_upload'),
]
