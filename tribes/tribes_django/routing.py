import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, ChannelNameRouter, URLRouter
from tribes_core.consumers import MessageConsumer, SysCommandConsumer
from django.urls import re_path

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter([
            re_path(r"^sys/command/feedback/$", SysCommandConsumer.as_asgi())
        ]),
    # Just HTTP for now. (We can add other protocols later.)
    "channel": ChannelNameRouter({
        "distribute_messages": MessageConsumer,
    })
})