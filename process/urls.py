from django.urls import path
from . import views

urlpatterns = [
    path('upload/motion/', views.upload_motion, name='upload_motion'),
    path('motion/user/<int:pk>',views.UserMotionList.as_view()),
]