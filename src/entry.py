import re
from js import Response
from urllib.parse import urlparse

## Example from: https://github.com/cloudflare/python-workers-examples/blob/main/03-fastapi/src/worker.py
## More: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
## Generic: https://developers.cloudflare.com/workers/languages/python/examples/
## Lang: https://developers.cloudflare.com/workers/languages/python/

async def on_fetch(request, env):
    url = urlparse(request.url)

    if url.path == "/":
        return Response.new("Hello, World!" )

    elif url.path == "/msg":
        return Response.new({
            "message": "Here is an example of getting an environment variable: "
            + env.MESSAGE
        })

    elif url.path == "/count" or url.path == "/count/":
        count = await env.EMOJI_API.get("count")
        await env.EMOJI_API.put("count", int(count) + 1)
        return Response.new({ "count": count })

    elif re.match(r"^/count/\d+$", url.path):
        match = re.search(r"/(\d+)$", url.path)
        num = int(match.group(1)) if match else 0
        
        await env.EMOJI_API.put("count", num)
        count = await env.EMOJI_API.get("count")
        return Response.new({ "count": count })
