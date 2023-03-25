from django.urls import path
from player.views import index

urlpatterns = [
    path('', index)
]