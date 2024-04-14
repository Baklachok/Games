from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import os
import django

from tic_tac_toe.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'games.settings')
django.setup()

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': URLRouter(websocket_urlpatterns),
})