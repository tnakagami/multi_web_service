from django.urls import path
from . import views

app_name = 'sns'

urlpatterns = [
    # Time line
    path('', views.TimeLineView.as_view(), name='time_line'),
    # Delete tweet
    path('delete_tweet/<int:pk>', views.DeleteTweetView.as_view(), name='tweet_delete'),
    # Search follower
    path('follower/search', views.SearchFollowerView.as_view(), name='search_follower'),
    # Create relationship
    path('follower/create', views.CreateRelationshipView.as_view(), name='create_follower'),
    # Delete relationship
    path('follower/delete/<int:pk>', views.DeleteRelationshipView.as_view(), name='delete_follower'),
]
