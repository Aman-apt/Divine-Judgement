
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
from math import floor, ceil
from statistics import mean
from typing import Sequence


class MaxRetriesExhaustedError(Exception):
    """Raise after the max_retries get's exahusted . """
    pass

@dataclass
class RequestResult:
    success: int
    url: str
    status_code: int
    connect_latency_ms: float
    ttfb_ms: float # time before the first bytes
    total_latency_ms: float
    timestamp: float
    error : str = None


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

                connect_latency_ms = (connect_end - start) * 1000 # <-- Miliseconds.
                total_latency_ms = (end - start) * 1000
                
                success, failure = 0, 0
                status_code = response.status
                if 200 <= status_code < 300:
                    success += 1
                    return RequestResult(
                        url=self.url,
                        status_code=status_code,
                        connect_latency=connect_latency_ms,
                        ttfb_ms=ttfb_ms,
                        total_latency_ms=total_latency_ms,
                        timestamp=start,
                        success=success,
                        error=cached_errors
                    )
                else:
                    failure += 1
                    cached_errors.append(f"attempt {attempt + 1}: HTTP {status_code}-- Failure:{failure}")

            except(aiohttp.ClientError, asyncio.TimeoutError) as e:
                cached_errors.append(f"attempt{attempt + 1} error: {e}")

            # Exponential backoff before retrying
            if attempt < self.max_retries - 1:
                wait = (2 ** attempt) + (attempt + 0.1)
                await asyncio.sleep(wait)

        raise MaxRetriesExhaustedError(
            f"{self.max_retries} are exahusted for {self.url}"
        )

    async def stop(self):
        """Stop the agent in the middle of excution. """
        pass
    
    async def memory(self):
        """Compute the memory usage of and based on time latnecy """
        pass

    async def send(self): # I will implement it later
        """
        Instead of just testing with get request we would be able to use laod tester for the PUT and POST as well.
        """
        pass


# Testing the functionalites of this thing .
if __name__ == "__main__":

    def percentile(values: Sequence[float], p: flaot) -> flaot:
        if not values:
            raise ValueError("Cannot compute values on the empty list")
        if not 0 <= p <= 100:
            raise ValueError("Perecentile must be between 0 to 100")

        data = [float(v) for v in values]
        n = len(data)

        if n == 1:
            return data[0] #return the first element
        
        # Linear interploation
        rank = (p / 100.0) * (n - 1)
        high = floor(rank)
        low = floor(rank)

        if low == high: # if they same exact value
            return low
            
        return data[low] + (data[high] - data[low]) * (rank - low)

    async def concurrent_agent(url: str, num_of_agent: int) -> RequestResult:
        semaphore = asyncio.Semaphore(min(700, num_of_agent))
        async with aiohttp.ClientSession() as session:
            request_agent = RequestAgent(url=url, session=session, semaphore=semaphore)
            task = [request_agent.run() for _ in range(num_of_agent)]
            results = await asyncio.gather(*task, return_exceptions=True)


        latencies = []
        failures = []

        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                failures.append((idx, str(result)))
                continue

            latency = getattr(result, "connect_latency", None)
            if latency is None:
                failures.append((idx, latency))
                continue

            try:
                latencies.append(float(latency))
            except (TypeError, ValueError):
                failures.append((idx, f"Invalid Latency value{latency!r}"))
        if not latencies:
            raise RuntimeError('No Latencies were found')

        stats = {
        "count": len(latencies),
        "failed": len(failures),
        "min": min(latencies),
        "max": max(latencies),
        "avg": mean(latencies),
        "p50": percentile(latencies, 50),
        "p90": percentile(latencies, 90),
        "p95": percentile(latencies, 95),
        "p99": percentile(latencies, 99),
        }

        return stats


    async def main():
        url = "https://techcrunch.com"
        local_url = "http://localhost:8080" 
        num_of_agent = 1000
        resp = await concurrent_agent(local_url, num_of_agent)
        print(resp)

    asyncio.run(main())
