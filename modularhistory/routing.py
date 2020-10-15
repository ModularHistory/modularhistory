# from django.conf.urls import url

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
# from chat.consumers import AdminChatConsumer, PublicChatConsumer
import chat.routing


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter(chat.routing.websocket_urlpatterns)
        # URLRouter([
        #     # url(r"^chat/admin/$", AdminChatConsumer),
        #     # url(r"^chat/$", PublicChatConsumer),
        # ])
    ),
})
