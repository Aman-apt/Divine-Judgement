
# A load manager that make's it possible to spawns N RequestAgent couroutines with
# asycio.gather .

import asyncio
import json
import csv
from re import L
import aiohttp
import time
from math import floor, ceil
from typing import Sequence, Type
from pathlib import Path
from agent import RequestAgent, RequestResult

class LoadTest:
    """
    A LoadTest class that spawns N RequestAgent coroutines with asyncio.gather, collects
    all RequestResult , then computes p50/p95/p99 latency, requests/sec and error rate.
    """

    def __init__(
        self,
        url: str, 
        num_of_agents: int,
        output_dir: str,
        semaphore: asyncio.Semaphore = 700,
        max_retries: int = 3,
        timeout: int = 10.0
    ) -> None:

        self.url = url
        self.num_of_agents = num_of_agents
        self.timeout = timeout
        self.results = RequestResult
        self.max_retries = max_retries
        self.semaphore = semaphore
        self.output_dir = Path(output_dir) #we have to fix so many things and add so many features i am getting excited

    def percentile(self, values: Sequence[float], p: float) -> float:
        if not values:
            raise ValueError('Cannot compute on empty list')
        if not 0 <= p <= 100:
            raise ValueError('Percentile must be between 0 to 100')

        data = sorted([float(v) for v in values])
        n = len(data)
        if n == 1:
            return data[0]

        # Linear ingestion
        rank = (p / 100.0) * (n - 1)
        low = floor(rank)
        high = ceil(rank)
        if low == high:
            return data[low]

        return data[low] + (data[high] - data[low]) * (rank - low)

    async def load_manager(self) -> list:

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/144.0.0.0 Safari/537.36" 
            )
        }

        # Trace the Http using aiohtt.TraceConfig
        async def on_request_start(session, context, params):
            context.start_time = session.loop.time()

        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)

        semaphore = asyncio.Semaphore(min(self.semaphore, self.num_of_agents))
        async with aiohttp.ClientSession(headers=headers, trace_configs=[trace_config]) as session:
            if self.num_of_agents <= 0:
                raise ValueError("Cannot Operate on the Negative or Zero Value")

            request_agent = RequestAgent(self.url, session, semaphore, self.timeout, self.max_retries)

            spawn_req_agent = [request_agent.run() for _ in range(self.num_of_agents)]
            agent_result = await asyncio.gather(*spawn_req_agent)
            print(agent_result)

            latencies = []
            failures = []
            for idx, result in enumerate(agent_result):
                if isinstance(result, Exception):
                    failure.append((idx, str(result)))
                    continue

                latency = getattr(result, "total_latency_ms", None)
                if latency is None:
                    failures.append((idx, result))
                    continue
                try:
                    latencies.append(float(latency))
                except(TypeError, ValueError):
                    failures.append((idx, f"Invalid latency {latency}"))
            if not latencies:
                raise RuntimeError("Latencies is Empty")

            # Export data to a file.
            file_path = self.output_dir
            extension = Path(file_path).suffix

            if extension == ".json":
                with open(self.output_dir, 'w') as f:
                    json.dump(agent_result, f, indent=5)

            elif extension == ".csv":
                with open(self.output_dir, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["id", "url", "status", "latenc_ms", "total_latency" \
                                                           "errors", "attempt", "cached_errors" ])
                    writer.writeheader()
                    writer.writerows(agent_result)
            else:
                with open("data.txt", 'w') as f:
                    data = f.write(agent_result)
                    return data
    
            stats = {
            "succes": success,
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

    async def graph():
        pass


# Testing the Functionality of the Class LaodTest

if __name__ == "__main__":
    async def main():
        num_agents = 1000
        url = "https://techcrunch.com"
        local_url = "http://localhost:8080"
        semaphore = 700
        output_dir = './data.csv'
        max_retries = 3
        timeout = 15
        load_test = LoadTest(url=local_url, num_of_agents=num_agents,semaphore=semaphore,\
                             output_dir=output_dir, max_retries=max_retries, timeout=timeout)
        load_manager = await load_test.load_manager()
        print(load_manager)

    asyncio.run(main())
