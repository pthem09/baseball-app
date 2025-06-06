from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('teams/', views.teams, name='teams'),
    path('player/', views.player, name='player'),
    path('games/', views.games, name='games'),
]
