

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

# 1) V1 -- Make 10 or 20k concurrent request to the same server .
# Solution -- I can make my own server and test on it and well it performs.
# I can use aiohttp lib to do that .
# Don't create a sessoin per request. Most likely i can do that in seperate
# or i can createa a different function to do just that.

import asyncio
from sys import exception
import aiohttp

# so the concurrenty problem is somewhat solved but we have anther proble which was expected .
# That is ClientTimeOutError :- As number of request increases time also increases . 
# How do i solve that . Q1) is this even problem that can be solved or it's is generally expected . ? 
# If it is solveable i need something ? i don't have any idea how am i going to solve this problem any how ?
# Well i have 10,000 task running, how many are actually doing network I/O at any single moment ?
# Not all 10,000. The event loop can only handle what the OS reports as ready via epoll 
# how do i control exactly how many requests are in-flight at any moment ?

async def make_single_request(url: str, session: aiohttp.ClientSession, semaphore: asyncio.Semaphore) -> int:
    # should we do this . but what would happen here .
    
    async with semaphore:
        async with session.get(url) as response:
            success, failure = 0, 0
        
            if response.status == 200:
                return response.status
            else:
                return response.status

async def worker(user_count: int):
    pass

async def make_conc_request(url: str, num_req: int = None) -> int:
    """
    Make a concurrrent request as to the server. Leverage the make_single_request function . 
    """
    req_count = 0

    headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
    }

    task_result = []

    semphaphore = asyncio.Semaphore(40)

    timeout = aiohttp.ClientTimeout(total=60)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        concurrent_list = [make_single_request(url, session, semphaphore) for _ in range(num_req)] #this is naive appraoch but it works
        task = asyncio.gather(*concurrent_list, return_exceptions=True)
        result = await task

        success, failure = 0, 0
        for status in result:
            req_count += 1 #count the request 
            if isinstance(status, Exception):
                failure += 1
            elif status == 200:
                success += 1
    return (f"Failuer: {failure} -- Success :{success}")

async def main():
    url = "https://techcrunch.com"
    req_per_test = 2000
    single_request = await make_conc_request(url, req_per_test)
    print(single_request)

asyncio.run(main())

