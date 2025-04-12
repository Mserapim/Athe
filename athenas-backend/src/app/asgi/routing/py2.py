from channels.routing import route
from default import websocket as ws


channel_routing = [
    route("websocket.receive", ws.ws_message),
    route("websocket.connect", ws.ws_connect),
    route("websocket.disconnect", ws.ws_disconnect),
]
