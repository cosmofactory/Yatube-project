from django.urls import path
from . import views


app_name = 'about'

urlpatterns = [
    path(r'author/', views.AboutAuthorView.as_view(), name='author'),
    path(r'tech/', views.AboutTechView.as_view(), name='tech'),
]
