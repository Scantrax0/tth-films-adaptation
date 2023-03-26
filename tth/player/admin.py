from django.contrib import admin

from player.models import VideoEntry

@admin.register(VideoEntry)
class VideoEntryAdmin(admin.ModelAdmin):
    fields = ['url']
