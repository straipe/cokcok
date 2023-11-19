from django.contrib import admin
from .models import Swing_Upload

@admin.register(Swing_Upload)
class SwingAdmin(admin.ModelAdmin):
    pass