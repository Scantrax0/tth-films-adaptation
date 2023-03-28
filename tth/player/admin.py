from django.contrib import admin

from player.models import VideoEntry

@admin.register(VideoEntry)
class VideoEntryAdmin(admin.ModelAdmin):
    list_display = ['id', 'url', 'status']
    fields = ['url']
