from django.urls import path
from . import views

urlpatterns = [
    path('achieve',views.AchievementList.as_view()),
    path('achieve/player',views.PlayerAchievementList.as_view()),
    path('match',views.MatchRecordList.as_view()),
    path('motion',views.PlayerMotionList.as_view()),
]