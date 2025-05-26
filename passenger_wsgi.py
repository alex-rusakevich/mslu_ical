from typing import cast

from a2wsgi import ASGIMiddleware
from a2wsgi.asgi_typing import ASGIApp

from src.main import app

application = ASGIMiddleware(cast(ASGIApp, app))
