

"""So far so good let's work with this and find out the limit of some projects """

"""
An HTTP laod tester is tool or sofware that simulates many concurrent users 
sending HTTP/HTTPS request to a web-server, API or application to measuer how it
performs under the traffic. The goal is to find performance limits, bottlenecks,
and stability issues before real user experciene them . 
"""
"""
What it does:
Throughput -- How many reequest per second the server can handle
Response time -- Latency at different load levels 
Error rate -- Success vs failure rates under the load
Capacity -- The point where perfromace degrades or the server crashes
scalability -- How well the system scales as the concurrent users increases . 
"""

# V2: Now let's start building the real thing ;
# Q1 — Throughput: Where do i put timer in my current code should i put a timer to measure total test duration, 
# and how do i turn that into requests per second?
# Q2 — Latency: This one's harder. I need to time each individual request, not the whole batch. 
# Where in the code does a single request start and end, and what data structure should i use to collect
# all 2000 individual timings so i can compute an average

import asyncio
from doctest import REPORT_NDIFF
import aiohttp
import time

# Throughput :- Le


async def make_single_request(
    url: str, 
    session: aiohttp.ClientSession,
    semaphore: asyncio.Semaphore,
    max_retries: int = 3
    ) -> int:

    """
    This is a base for making concurrent request and it's whole functionality .
    Depends on the effiecy of this fucntion . 
    """
    catched_errors = []
    start_timer = time.perf_counter()
    for attempt in range(max_retries):
        try:
            async with semaphore:
                async with session.get(url) as response:
                    status = response.status
                    if status == 200:
                        end_timer = time.perf_counter()
                        result = end_timer - start_timer
                        return ((status), result) # why the fuck it's happening
                    else:
                        catched_errors.append(response.status)

        except(aiohttp.ClientError, asyncio.TimeoutError) as e:
            wait = (2 * attempt) + (attempt * 0.1)

            if attempt == max_retries - 1:
                print(f"Retry {attempt + 1} after {wait} time: {e}")
                await asyncio.sleep(wait)

                raise Exception(f"Numbers of retries {max_retries} has been exahusted")

async def worker(user_count: int):
    pass

async def make_conc_request(url: str, num_req: int = None) -> str:
    """
    Make a concurrrent request as to the server. Leverage the make_single_request function . 
    """
    req_count = 0

    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    task_result = []

    semphaphore = asyncio.Semaphore(700)

    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        concurrent_list = [make_single_request(url, session, semphaphore) for _ in range(num_req)] 
        task = asyncio.gather(*concurrent_list, return_exceptions=True)
        result = await task 

        success, failure = 0, 0
        for status, time in result:
            req_count += 1
            if isinstance(status, Exception):
                failure += 1
            elif status == 200:
                success += 1
    return (f"Failuer: {failure} -- Success :{success} -- Timer : {time}")


async def main():
    url = "https://techcrunch.com"
    local_url = "http://localhost:8080" 
    req_per_test = 50000
    single_request = await make_conc_request(local_url, req_per_test)
    print(single_request)

asyncio.run(main())

