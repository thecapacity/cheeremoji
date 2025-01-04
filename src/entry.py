import re
import json
import unicodedata
from urllib.parse import urlparse, parse_qs, unquote

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
        console.log(f"loadMap: {map}")
    return

async def is_valid_emoji(emoji):
    return emoji in map.values()

async def is_valid_code(code):
    return code in map.keys()

async def get_cheeremoji(env):
    shortcode = await env.EMOJI_API.get("code")
    emoji = map[shortcode]
    
    data = {
        'emoji': emoji,
        'code': shortcode
    }
    return data

async def handle_get_cheeremoji(request, env):
    data = await get_cheeremoji(env)
    return Response.new(data, headers=[("content-type", "application/json")])

async def handle_get_cheeremoji_emoji(request, env):
    data = await get_cheeremoji(env)
    return Response.new({ "emoji": data["emoji"] }, headers=[("content-type", "application/json")])

async def handle_get_cheeremoji_code(request, env):
    data = await get_cheeremoji(env)
    return Response.new({ "code": data["code"] }, headers=[("content-type", "application/json")])

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

async def set_cheeremoji_emoji(env, emoji):
    code = next((key for key, value in map.items() if value == emoji), None)
    if await is_valid_code(code):
        console.log(f"Setting emoji to: {code} -> {emoji}")
        await env.EMOJI_API.put("code", code)
    return

async def set_cheeremoji_code(env, code):
    if await is_valid_code(code):
        console.log(f"Setting emoji to code: {code}")
        await env.EMOJI_API.put("code", code)
    return

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
        
        elif request.method == "GET" and re.match(r"^/emoji/.+/?$", url.path.lower()):
            ## FIXME: Find a better way to parse the emoji from the URL so it doesn't end up as hex
            path = url.path.strip("/").split("/")
            emoji = path[1]
            return Response.new({ emoji, await is_valid_emoji(emoji) }, headers=[("content-type", "application/json")])

        elif request.method == "GET" and re.match(r"^/code/.+/?$", url.path.lower()):
            ## FIXME: Find a better way to parse the shortcode from the URL - with or without the colon
            path = url.path.strip("/").split("/")
            code = path[1]
            code = code.replace(":", "").lower()
            code = f":{code}:"

            console.log(f"Checking Code: {code}")
            
            if await is_valid_code(code):
                await set_cheeremoji_code(env, code)
                return Response.new({ code }, headers=[("content-type", "application/json")], status=200)
            else:
                return Response.new({ code }, headers=[("content-type", "application/json")], status=404)

        else:
            return Response.new("Path Not Found", status=404)

    except Exception as e:
        error_details = traceback.format_exc() # Include the traceback in the response
        return Response.new(f"Error: {str(e)}\n\nDetails:\n{error_details}", status=500)

