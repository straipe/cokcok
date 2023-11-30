from django.urls import path
from . import views

urlpatterns = [
    path('player/info/<str:pk>',views.PlayerInfo.as_view()),
]