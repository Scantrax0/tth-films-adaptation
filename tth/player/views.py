from django.shortcuts import render
from django.views import generic
from player.models import VideoEntry

class IndexView(generic.ListView):
    template_name = 'player/index.html'
    context_object_name = 'video_list'
    model = VideoEntry
    ordering = ['-pk']

class PlayerView(generic.DetailView):
    model = VideoEntry
    template_name = 'player/player.html'