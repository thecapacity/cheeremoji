import re
from urllib.parse import urlparse, parse_qs
import traceback

from js import Response, Object, Headers, JSON, console, fetch

## Example from: https://github.com/cloudflare/python-workers-examples/blob/main/03-fastapi/src/worker.py
##    - https://developers.cloudflare.com/workers/examples/
## More: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
## Generic: https://developers.cloudflare.com/workers/languages/python/examples/
## Lang: https://developers.cloudflare.com/workers/languages/python/
## Logging: https://developers.cloudflare.com/workers/languages/python/examples/#emit-logs-from-your-python-worker

async def handle_main(request, env):
    ## https://developers.cloudflare.com/workers/examples/fetch-json/
    ## NOTE: even if it's a local JSON file in env.ASSETS you still have to env.ASSETS.fetch("http://localhost:port/file.json")
    async def gather_response(response):
        headers = response.headers
        content_type = headers["content-type"] or ""

        if "application/json" in content_type:
            return (content_type, JSON.stringify(await response.json()))
        return (content_type, await response.text())

    response = await fetch("https://cheeremoji.com/emojiMap.json")
    content_type, result = await gather_response(response)

    headers = Headers.new({"content-type": content_type}.items())

    console.log(f"result: {result}")

    return Response.new(result, headers=headers)

async def get_count(request, env):
    count = await env.EMOJI_API.get("count")
    await env.EMOJI_API.put("count", int(count) + 1)
    return Response.new({ "count": count })

async def set_count_get(request, env):
    url = urlparse(request.url)
    
    match = re.search(r"/(\d+)$", url.path)
    num = int(match.group(1)) if match else 0
    
    await env.EMOJI_API.put("count", num)
    count = await env.EMOJI_API.get("count") ## may not be necessary but may guard against concurrent updates

    return Response.new({ "count": count })

async def set_count_post(request, env):
    data = await request.json()
    num = data.count
    
    if num:
        console.log(f"POST SET - num: {num}")
        await env.EMOJI_API.put("count", num)
    
    count = await env.EMOJI_API.get("count") ## may not be necessary but may guard against concurrent updates
    return Response.new({ "count": count })

async def on_fetch(request, env):
    url = urlparse(request.url)
    params = parse_qs(url.query)

    ## Parsing JSON: data = (await request.json())
    ## https://developers.cloudflare.com/workers/languages/python/examples/#parse-json-from-the-incoming-request

    #console.log(f"pyodide Version: {pyodide.__version__}")
    #console.log(f"{dir(pyodide.ffi)}")
    console.log(f"Handling fetch: {url.path}")
    console.log(f"Method: {request.method}")
    console.log(f"Parms: {params}")
    ##console.log(f"{dir(env.ASSETS)}")

    try:
        if url.path == "/":
            return await handle_main(request, env)
        
        elif request.method == "GET" and (url.path == "/count" or url.path == "/count/"):
            return await get_count(request, env)
        
        elif request.method == "GET" and re.match(r"^/count/\d+$", url.path):
            return await set_count_get(request, env)

        elif request.method == "POST" and (url.path == "/count" or url.path == "/count/"):
            return await set_count_post(request, env)

        else:
            return Response.new("Path Not Found", status=404)

    except Exception as e:
        error_details = traceback.format_exc() # Include the traceback in the response
        return Response.new(f"Error: {str(e)}\n\nDetails:\n{error_details}", status=500)

