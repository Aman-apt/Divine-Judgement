
# Agent is simulation of a real user like request to the server .
# It's a single request that returns a status code or error

import uuid
import asyncio
import aiohttp
from dataclasses import dataclass, field
import time

@dataclass
class RequestResult:
    agent_id: str
    url: str
    status: int
    latecy_ms: float
    connect_latency: float
    attempt: int
    error : str = None
    cached_errors: list[str] = None


class RequestAgent:
    """
    Simulate a single user request with retries, latency tracking and concurrency 
    with async semaphore
    """

    def __init__(
        self,
        url: str,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        max_retries: int = 3,
        timeout: float = 10.0
    ):

        self.id: int = uuid(uuid)
        self.url = url
        self.session = session
        self.max_retries = max_retries
        self.semaphore = semaphore
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def run(self) -> RequestResult:
        pass
