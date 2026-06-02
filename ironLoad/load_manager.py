
# A load manager that make's it possible to spawns N RequestAgent couroutines with
# asycio.gather .

import asyncio
import json
import csv
import aiohttp
import time
from pathlib import Path
from agent import RequestAgent

class LoadTest:
    """
    A LoadTest class that spawns N RequestAgent coroutines with asyncio.gather, collects
    all RequestResult , then computes p50/p95/p99 latency, requests/sec and error rate.
    """

    def __init__(
        self,
        url: str, 
        num_of_agents: int,
        timeout: int = 10.0,
        output_dir: str,
        semaphore: asyncio.Semaphore,
        max_retries: int = 3
    ) -> None:

        self.url = url
        self.num_of_agents = num_of_agents
        self.timeout = timeout
        self.results = RequestResult
        self.max_retries = max_retries
        self.semaphores = semaphore
        self.output_dir = Path(output_dir) #we have to fix so many things and add so many features i am getting excited

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

        semaphore = asyncio.Semaphore(700) 
        async with aiohttp.ClientSession(headers=headers) as session:
            request_agent = RequestAgent(self.url, session, semaphore, self.timeout, self.max_retries)

            spawn_req_agent = [request_agent.run() for _ in range(self.num_of_agents)]
            task_req = asyncio.gather(*spawn_req_agent)
            req_result = await task_req

            # Now i can access the individual attributes of ReqquestResult
            for data in req_result:
                latency = sorted(data.latecy_ms)
                print(latency)

            # how do i perform p50 and p99.

            # Export data to a json file
            file_path = self.output_dir
            extension = Path(file_path).suffix

            if extension == ".json":
                with open(self.output_dir, 'w') as f:
                    json.dump(req_result, f, indent=5)

            elif extension == ".csv":
                with open(self.output_dir, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["id", "url", "status", "latenc_ms", "total_latency" \
                                                           "errors", "attempt", "cached_errors" ])
                    writer.writeheader()
                    writer.writerows(req_result)
            else:
                with open("data.txt", 'w') as f:
                    data = f.write(req_result)
                    return data
