from collections.abc import AsyncGenerator

from aiohttp import ClientSession
from fake_useragent import UserAgent

ua = UserAgent()


async def get_http_session() -> AsyncGenerator[ClientSession, None]:
    headers = {
        "User-Agent": ua.random,
        "Accept": "application/json"
    }
    
    async with ClientSession(
        headers=headers
    ) as session:
        yield session