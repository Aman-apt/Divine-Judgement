

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
import aiohttp


# Make 20 concurrent request to the same url and receive the 200
# so function_make_single_request returns an int and we can't create task or gather task on int , we need iterable but how?
# should we use while loop for sessiong . ? 
# Let's break down the problem here , we have to do three things here:- 1) A succesfull single req , 2) Make this request concurrent?
# What do i made my concurrent that non-blocking i meant by that . Let's try to make this happnen but how ? 
# No clue :-

async def make_single_request(url: str, session: aiohttp.ClientSession) -> int:
    # should we do this . but what would happen here . the while loop will not make a concurrent_request in here i think we should try on the conc
    async with session.get(url) as response:
        status = response.status
        if status == 200:
            return status
        else:
            raise aiohttp.ClientError("The response was either 400 or 500 status code .")



async def make_conc_request(url: str, num_req: int = None) -> int:
    """
    Make a concurrrent request as to the server. Leverage the make_single_request function . 
    """
    req_count = 0 #count the number of request to the server per second .

    headers = {"User-Agent": ""}
    timeout = aiohttp.ClientTimeout(total=10)
    async with aiohttp.ClientSession(headers=headers, timeout=timeout) as session:
        response = await make_single_request(url, session)
        if response:
            req_count += 1
            return response
        else:
            return aiohttp.ServerConnectionError('No 200_OK response from the server')
    return req_count

async def main():
    url = "https://techcrunch.com"
    single_request = await make_conc_request(url)
    
    num_of_req = 0
    for req in range(200):
        task_req = await make_conc_request(url) # hammer that server 200 times? is this concurrent i don't think so .
        print(task_req)
        num_of_req += 1
    return num_of_req


    
asyncio.run(main())

