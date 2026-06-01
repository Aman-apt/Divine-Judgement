

# Server to test the latency on the real server which is not in production .
# It does not have CDN and ratelimiting .

from aiohttp import web 

async def handle(request):
    return web.Response(text="OK")

app = web.Application()
app.router.add_get("/", handle)
web.run_app(app, port=8080)

