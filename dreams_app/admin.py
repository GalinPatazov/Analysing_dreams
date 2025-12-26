from django.contrib import admin

from dreams_app.models import Dream


# Register your models here.
@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    ordering = ('-created_at',)