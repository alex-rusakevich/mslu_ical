from a2wsgi import ASGIMiddleware

from mslu_ical import app

application = ASGIMiddleware(app)
