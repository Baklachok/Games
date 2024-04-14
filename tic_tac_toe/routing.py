from django.urls import path
from . import consumer

websocket_urlpatterns = [
    path('ws/game/<int:game_id>/', consumer.GameConsumer.as_asgi()),
]


