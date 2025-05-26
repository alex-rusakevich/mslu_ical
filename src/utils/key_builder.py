from logging import getLogger

from fastapi_cache import default_key_builder

logger = getLogger("uvicorn.error")


def ignore_session_key_builder(*args, **kwargs):
    #logger.debug(str(args) + " " + str(kwargs))

    kwargs['kwargs'] = {k: v for k, v in kwargs['kwargs'].items() if not k == 'session'}
    #logger.debug(str(args) + " " + str(kwargs))

    return default_key_builder(*args, **kwargs)