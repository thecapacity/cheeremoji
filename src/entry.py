from fastapi import FastAPI, Request
from pydantic import BaseModel

## Example from: https://github.com/cloudflare/python-workers-examples/blob/main/03-fastapi/src/worker.py
## More: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
## Generic: https://developers.cloudflare.com/workers/languages/python/examples/
## Lang: https://developers.cloudflare.com/workers/languages/python/

async def on_fetch(request, env):
    import asgi
    return await asgi.fetch(app, request, env)

app = FastAPI()

@app.get("/")
async def root():
    return { "message": "Hello, World!" }

@app.get("/msg")
async def msg(req: Request):
    env = req.scope["env"]
    return {
        "message": "Here is an example of getting an environment variable: "
        + env.MESSAGE
    }

@app.get("/count")
async def get_count(req: Request):
    env = req.scope["env"]
    count = await env.EMOJI_API.get("count")
    await env.EMOJI_API.put("count", int(count) + 1)
    return { "count": count }

@app.get("/count/{num}")
async def read_count(req: Request, num: int | None = 0):
    env = req.scope["env"]
    await env.EMOJI_API.put("count", num)
    count = await env.EMOJI_API.get("count")
    return { "count": count }
