from django.urls import path
from . import views

urlpatterns = [
    path('achievement',views.AchievementList.as_view()),
    path('motion/player/<str:pk>',views.PlayerMotionList.as_view()),
    path('motion/detail/<str:pk1>/<int:pk2>',views.PlayerMotionDetail.as_view()),
]