from django.urls import path
from .consumers import ChatConsumer

wsPattern = [path("ws/messages/<int:room_name>/", ChatConsumer.as_asgi())]