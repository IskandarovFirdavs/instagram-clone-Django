import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

from chat.routing import wsPatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'instagram_clone.settings')

http_response = get_asgi_application()

application = ProtocolTypeRouter({
    'http': http_response,
    'websocket': URLRouter(wsPatterns)
})

