from fastapi.middleware.wsgi import WSGIMiddleware

from mslu_ical import app

application = WSGIMiddleware(app)
