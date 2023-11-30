from django.urls import path
from . import views

urlpatterns = [
    path('motion/player/<str:pk>',views.PlayerMotionList.as_view()),
    path('achievement',views.AchievementList.as_view()),
    path('player/info/<str:pk>',views.PlayerInfo.as_view()),
]