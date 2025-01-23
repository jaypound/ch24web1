from django.contrib import admin
from .models import Program, Episode, Creator
from .models import HomeMessage

# Register your models here.
admin.site.register(Program)
admin.site.register(Episode)
admin.site.register(Creator)


@admin.register(HomeMessage)
class HomeMessageAdmin(admin.ModelAdmin):
    list_display = ['message', 'is_active', 'created_at']
    list_editable = ['is_active']