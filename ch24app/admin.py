from django.contrib import admin
from .models import Program, Episode, Creator

# Register your models here.
admin.site.register(Program)
admin.site.register(Episode)
admin.site.register(Creator)