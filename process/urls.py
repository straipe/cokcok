from django.urls import path
from . import views

urlpatterns = [
    path('upload/swing/', views.upload_swing, name='upload_swing'),
    path('swing_list/',views.swing_list, name='swing_list'),
]