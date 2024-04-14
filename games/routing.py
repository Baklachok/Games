from channels.routing import ProtocolTypeRouter

from tic_tac_toe.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "websocket": websocket_urlpatterns,
})