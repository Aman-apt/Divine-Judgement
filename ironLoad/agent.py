
# Agent is simulation of a real user like request to the server .
# It's a single request that returns a status code, error, latecy and total latecy

"""
Cleaner and better version of the make_single_reqeust().
Core Functionalites has been implemeted but still there are 2 or 3 things to implement
"""

import uuid
import asyncio
import aiohttp
from dataclasses import dataclass, field
import time

class MaxRetriesExhaustedError(Exception):
    """Raise after the max_retries get's exahusted . """
    pass

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
    with async semaphore. 
    """

    def __init__(
        self,
        url: str,
        session: aiohttp.ClientSession,
        semaphore: asyncio.Semaphore,
        max_retries: int = 3,
        timeout: float = 10.0
    ):

        self.id: int = str(uuid.uuid4())
        self.url = url
        self.session = session
        self.max_retries = max_retries
        self.semaphore = semaphore
        self.timeout = aiohttp.ClientTimeout(total=timeout)

    async def run(self) -> RequestResult:
        cached_errors = []
        for attempt in range(self.max_retries):
            try:
                start = time.perf_counter()
                connect_end = None

                async with self.semaphore:
                    async with self.session.get(url=self.url, timeout=self.timeout) as response:
                        connect_end = time.perf_counter()
                        await response.read()
                        end = time.perf_counter()

                connect_latency_ms = (connect_end - start) # this is milliseconds
                total_latecy_ms = (end - start)

                status = response.status
                if 200 <= status < 300:
                    return RequestResult(
                        agent_id=self.id,
                        url=self.url,
                        status=status,
                        connect_latency=connect_latency_ms,
                        latecy_ms=total_latecy_ms,
                        attempt=attempt + 1,
                        cached_errors=cached_errors
                    )
                else:
                    cached_errors.append(f"attempt {attempt + 1}: HTTP {status}")

            except(aiohttp.ClientError, asyncio.TimeoutError) as e:
                cached_errors.append(f"attempt{attempt + 1} error: {e}")

            # Exponential backoff before retrying
            if attempt < self.max_retries - 1:
                print(attempt, self.max_retries)
                wait = (2 ** attempt) + (attempt + 0.1)
                await asyncio.sleep(wait)

        raise MaxRetriesExhaustedError(
            f"{self.max_retries} are exahusted for {self.url}"
        )
    
    async def memory(self):
        pass


# Testing the functionalites of this thing .
if __name__ == "__main__":

    async def concurrent_agent(url: str, num_of_agent: int) -> RequestResult:
        semaphore = asyncio.Semaphore(700)
        async with aiohttp.ClientSession() as session:
            request_agent = RequestAgent(url=url, session=session, semaphore=semaphore)
            task = [request_agent.run() for _ in range(num_of_agent)]
            result = asyncio.gather(*task)
            data = await result
        return (f"{data[-1]}, Number of Agents: {num_of_agent} .")

    async def main():
        url = "https://techcrunch.com"
        local_url = "http://localhost:8080" 
        num_of_agent = 100000
        resp = await concurrent_agent(local_url, num_of_agent)
        print(resp)

    asyncio.run(main())
