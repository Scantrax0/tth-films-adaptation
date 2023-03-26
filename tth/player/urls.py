from django.urls import path
from player.views import IndexView, PlayerView

urlpatterns = [
    path('', IndexView.as_view(), name="index"),
    path('<int:pk>/', PlayerView.as_view(), name="player")
]