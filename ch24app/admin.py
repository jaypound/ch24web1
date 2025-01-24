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

from django.contrib import admin
from .models import StreamSettings

@admin.register(StreamSettings)
class StreamSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_stream_active', 'updated_at']
    list_editable = ['is_stream_active']
    
    def has_add_permission(self, request):
        return not StreamSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False