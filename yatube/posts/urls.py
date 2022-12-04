from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path(r'', views.index, name='index'),
    path(r'group/<slug:slug>/', views.group_posts, name='group_list'),
    path(r'posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path(r'profile/<str:username>/', views.profile, name='profile'),
    path(r'create/', views.post_create, name='post_create'),
    path(r'posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path(
        r'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment'
    ),
    path(r'follow/', views.follow_index, name='follow_index'),
    path(
        r'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow'
    ),
    path(
        r'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
