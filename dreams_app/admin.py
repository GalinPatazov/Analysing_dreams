from django.contrib import admin
from .models import Dream, Favorite, AIAnalysisDailyUsage


@admin.register(Dream)
class DreamAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at')
    ordering = ('-created_at',)
    search_fields = ('user__username', 'name')
    list_filter = ('created_at',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'dream', 'created_at')
    search_fields = ('user__username', 'dream__name')


@admin.register(AIAnalysisDailyUsage)
class AIAnalysisDailyUsageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'count')
    list_filter = ('date',)
    search_fields = ('user__username',)