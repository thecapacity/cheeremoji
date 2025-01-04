import re
import json
from urllib.parse import urlparse, parse_qs
import traceback

from js import Response, Object, Headers, JSON, console, fetch

## Example from: https://github.com/cloudflare/python-workers-examples/blob/main/03-fastapi/src/worker.py
##    - https://developers.cloudflare.com/workers/examples/
## More: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
## Generic: https://developers.cloudflare.com/workers/languages/python/examples/
## Lang: https://developers.cloudflare.com/workers/languages/python/
## Logging: https://developers.cloudflare.com/workers/languages/python/examples/#emit-logs-from-your-python-worker

## emoji/🥇
## :1st_place_medal:

map = None
async def loadMap():
    global map   
    if map is None:
        getMapResponse = await fetch("https://cheeremoji.com/emojiMap.json")
        MapData = JSON.stringify(await getMapResponse.json())
        map = json.loads(MapData)
        map.update({"205": "MYVALUEs"})

    return

async def handle_get_map(request, env):
    """    Handle the main request for the Emoji Map via the / path.    """
    ## https://developers.cloudflare.com/workers/examples/fetch-json/
    ## NOTE: even if it's a local JSON file in env.ASSETS you still have to env.ASSETS.fetch("http://localhost:port/file.json")
    ## NOTE: might as well just get it from the static site
    ## FIXME: When this is called maybe we should update the global map data too

    async def gather_response(response):
        headers = response.headers
        content_type = headers["content-type"] or ""

        if "application/json" in content_type:
            return (content_type, JSON.stringify(await response.json()))
        return (content_type, await response.text())

    response = await fetch("https://cheeremoji.com/emojiMap.json")
    content_type, result = await gather_response(response)

    headers = Headers.new({"content-type": content_type}.items())

    console.log(f"getMap: {result}")

    return Response.new(result, headers=headers)

async def get_cheeremoji(env):
    emoji = await env.EMOJI_API.get("count")
    shortcode = map[emoji]
    
    data = {
        'emoji': emoji,
        'code': shortcode
    }
    return data

async def set_cheeremoji(env, emoji):
    await env.EMOJI_API.put("count", "🥇")
    return await get_cheeremoji(env)

async def handle_get_cheeremoji(request, env):
    data = await get_cheeremoji(env)
    return Response.new(data, headers=[("content-type", "application/json")])

async def handle_get_cheeremoji_emoji(request, env):
    data = await get_cheeremoji(env)
    return Response.new({ "emoji": data["emoji"] }, headers=[("content-type", "application/json")])

async def handle_get_cheeremoji_code(request, env):
    data = await get_cheeremoji(env)
    return Response.new({ "code": data["code"] }, headers=[("content-type", "application/json")])

async def on_fetch(request, env):
    global map
    await loadMap()

    url = urlparse(request.url)
    params = parse_qs(url.query)

    ## Parsing JSON: data = (await request.json())
    ## https://developers.cloudflare.com/workers/languages/python/examples/#parse-json-from-the-incoming-request

    #console.log(f"pyodide Version: {pyodide.__version__}")
    #console.log(f"{dir(pyodide.ffi)}")
    console.log(f"Handling fetch: {url.path}")
    console.log(f"Method: {request.method}")
    console.log(f"Parms: {params}")
    console.log(f"nData: {len(map.keys())}")
    
    ##console.log(f"{dir(env.ASSETS)}")

    try:
        if request.method == "GET" and (url.path == "/" or url.path == ""):
            return await handle_get_cheeremoji(request, env)

        elif request.method == "GET" and re.match(r"^/emoji/?$", url.path.lower()):
            return await handle_get_cheeremoji_emoji(request, env)

        elif request.method == "GET" and re.match(r"^/code/?$", url.path.lower()):
            return await handle_get_cheeremoji_code(request, env)

        elif request.method == "GET" and url.path.lower().strip("/") == "/map":
            return await handle_get_map(request, env)
        

        else:
            return Response.new("Path Not Found", status=404)

    except Exception as e:
        error_details = traceback.format_exc() # Include the traceback in the response
        return Response.new(f"Error: {str(e)}\n\nDetails:\n{error_details}", status=500)

