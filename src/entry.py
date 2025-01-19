import re
import json
import unicodedata

from functools import partial
from urllib.parse import urlparse, parse_qs, unquote

import traceback

from js import Response, Object, Headers, JSON, console, fetch, WebSocketPair
from asgi import process_websocket as app, request_to_scope

## Example from: https://github.com/cloudflare/python-workers-examples/blob/main/03-fastapi/src/worker.py
##    - https://developers.cloudflare.com/workers/examples/
## More: https://developers.cloudflare.com/workers/languages/python/packages/fastapi/
## Generic: https://developers.cloudflare.com/workers/languages/python/examples/
## Lang: https://developers.cloudflare.com/workers/languages/python/
## Logging: https://developers.cloudflare.com/workers/languages/python/examples/#emit-logs-from-your-python-worker

## emoji/🥇
## :1st_place_medal:

from pyodide.ffi import to_js as _to_js
# to_js converts between Python dictionaries and JavaScript Objects
def to_js(obj):
   return _to_js(obj, dict_converter=Object.fromEntries)

map = None
async def loadMap():
    global map   
    if map is None:
        getMapResponse = await fetch("https://cheeremoji.com/static/emojiMap.json", {
            "headers": {
            "Content-Type": "application/json"
            }
        })
        MapData = JSON.stringify(await getMapResponse.json())
        map = json.loads(MapData)
        console.log(f"loadMap: {len(map.keys())}")
    return

async def is_valid_emoji(emoji):
    return emoji in map.values()

async def is_valid_code(code):
    return code in map.keys()

async def get_cheeremoji(env):
    shortcode = await env.EMOJI_API.get("code")
    emoji = map[shortcode]
    
    data = {
        "emoji": emoji,
        "code": shortcode
    }
    return data

async def handle_get_cheeremoji(request, env, response_headers):
    data = await get_cheeremoji(env)
    return Response.new( json.dumps(data), headers=response_headers, status=200)

async def handle_get_cheeremoji_emoji(request, env, response_headers):
    data = await get_cheeremoji(env)
    return Response.new( json.dumps({ "emoji": data["emoji"] }), headers=response_headers, status=200)

async def handle_get_cheeremoji_code(request, env, response_headers):
    data = await get_cheeremoji(env)
    return Response.new( json.dumps({ "code": data["code"] }), headers=response_headers, status=200)

async def handle_get_map(request, env, response_headers):
    """    Handle the main request for the Emoji Map via the / path.    """
    """    NOTE: NOT USED ANYMORE!                                      """
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

    #console.log(f"getMap: {result}")

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

async def process_websocket(app, req):
    client, server = WebSocketPair.new().object_values()
    server.accept()
    queue = Queue()

    def onopen(evt):
        msg = {"type": "websocket.connect"}
        queue.put_nowait(msg)

    # onopen doesn't seem to get called. WS lifecycle events are a bit messed up
    # here.
    onopen(1)

    def onclose(evt):
        msg = {"type": "websocket.close", "code": evt.code, "reason": evt.reason}
        queue.put_nowait(msg)

    def onmessage(evt):
        msg = {"type": "websocket.receive", "text": evt.data}
        queue.put_nowait(msg)

    server.onopen = onopen
    server.onopen = onclose
    server.onmessage = onmessage

    async def ws_send(got):
        if got["type"] == "websocket.send":
            b = got.get("bytes", None)
            s = got.get("text", None)
            if b:
                with acquire_js_buffer(b) as jsbytes:
                    # Unlike the `Response` constructor,  server.send seems to
                    # eagerly copy the source buffer
                    server.send(jsbytes)
            if s:
                server.send(s)

        else:
            print(" == Not implemented", got["type"])

    async def ws_receive():
        received = await queue.get()
        return received

    env = {}
    run_in_background(app(request_to_scope(req, env, ws=True), ws_receive, ws_send))

    return Response.new(None, status=101, webSocket=client)



async def on_fetch(request, env):
    global map
    await loadMap()
    if False and not hasattr(env, 'background_task'):
        async def background_task():
            while True:
                await broadcast_update(env)
                await asyncio.sleep(60)  # Adjust the interval as needed

        env.background_task = asyncio.create_task(background_task())
    response_headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Access-Control-Allow-Origin", "*"),
        ("Access-Control-Allow-Methods", "GET, POST, OPTIONS"),
        ("Access-Control-Allow-Headers", "Content-Type, Authorization")
    ]

    url = urlparse(request.url)
    params = parse_qs(url.query)

    ## Parsing JSON: data = (await request.json())
    ## https://developers.cloudflare.com/workers/languages/python/examples/#parse-json-from-the-incoming-request

    #console.log(f"pyodide Version: {pyodide.__version__}")
    #console.log(f"{dir(pyodide.ffi)}")
    console.log(f"Handling {request.method} for: {url.path}")
    #console.log(f"Parms: {params}")
    #console.log(f"nData: {len(map.keys())}")
    
    ##console.log(f"{dir(env.ASSETS)}")

    try:
        if request.method == "GET" and (url.path == "/" or url.path == ""):
            return await handle_get_cheeremoji(request, env, response_headers)

        elif request.method == "GET" and url.path.lower() == "/ws":
            #console.log(f"WebSocket client connected: {request.url}")
            console.log(f"Websocket Headers: {dict(request.headers)}")
            #console.log(f"Request Method: {request.method}")
            #console.log(f"Request Params: {params}")
    
            if request.headers.get("Upgrade", None) == "websocket":
                web_socket_pair = WebSocketPair.new(request)
                client, server = Object.values(web_socket_pair)

                #console.log(f"WebSocket Pair: {web_socket_pair}")
                console.log(f"\tWebSocket Client: {dir(client)}")
                console.log(f"\tWebSocket Server: {dir(server)}")

                server.accept()
                if not hasattr(env, 'clients'):
                    env.clients = []
                env.clients.append(server)

                console.log("a")

                async def handle_message(event, server, env):
                    try:
                        console.log(f"Message event: {event.data}")
                        message = await get_cheeremoji(env)
                        return server.send(message)

                    except Exception as e:
                        console.log(f"Error sending message: {e}")

                async def handle_close(event, server, env):
                    try:
                        console.log(f"Close event: {event.code}, {event.reason}")
                        env.clients.remove(server)
                        return server.close(1000, "CheerEmoji Closing")
                    except Exception as e:
                        console.log(f"Error during close: {e}")

                console.log("b")

                #server.addEventListener("message", partial(handle_message, server=server, env=env))
                #server.addEventListener("close", partial(handle_close, server=server, env=env))

                #server.addEventListener("message", lambda event: asyncio.run(handle_message(event, server, env)))
                #server.addEventListener("close", lambda event: asyncio.run(handle_close(event, server, env)))

                #server.addEventListener("message", lambda event: asyncio.run(handle_message(env, server)))
                #server.addEventListener("close", lambda event: asyncio.run(handle_close(env, server)))

                console.log("c")

                return Response.new(None, { "status": 101, "webSocket": client }, headers=response_headers, status=101)
            else:
                return Response.new("Not a websocket request", { "status": 426 })

        #elif request.method == "GET" and url.path.lower().strip("/") == "/map":
        #    return await handle_get_map(request, env, response_headers)

        elif request.method == "GET" and re.match(r"^/emoji/?$", url.path.lower()):
            return await handle_get_cheeremoji_emoji(request, env, response_headers)

        elif request.method == "GET" and re.match(r"^/code/?$", url.path.lower()):
            return await handle_get_cheeremoji_code(request, env, response_headers)
        
        elif request.method == "GET" and re.match(r"^/emoji/.+/?$", url.path.lower()):
            path = url.path.strip("/").split("/")
            emoji = unquote(path[1]) ## Emojis are passed in as percent-encoded format 
            emoji = unicodedata.normalize("NFC", emoji.strip()) #NFC: Composes characters into their canonical form (recommended for matching).

            if await is_valid_emoji(emoji):
                await set_cheeremoji_emoji(env, emoji)
            else:
                console.log(f"GET BAD EMOJI: {url.path}")
                console.log(f"GET BAD EMOJI Headers: {dict(request.headers)}")
                console.log(f"GET BAD EMOJI: {emoji}")
            
            return await handle_get_cheeremoji(request, env, response_headers)

        elif request.method == "GET" and re.match(r"^/code/.+/?$", url.path.lower()):
            path = url.path.strip("/").split("/")
            code = unquote(path[1])
            code = code.replace(":", "")
            code = f":{code}:"
            
            if await is_valid_code(code):
                await set_cheeremoji_code(env, code)
            else:
                console.log(f"GET BAD CODE PATH: {url.path}")
                console.log(f"GET BAD CODE Headers: {dict(request.headers)}")
                console.log(f"GET BAD CODE: {code}")
            
            return await handle_get_cheeremoji(request, env, response_headers)
        
        elif request.method == "OPTIONS":
            return Response.new("", headers=response_headers, status=200)
        
        elif request.method == "POST":
            data = await request.json()
            data = data.to_py()

            console.log(f"POST Data: {data}")
            
            if isinstance(data, dict):
                emoji = data.get("emoji", None)
                code = data.get("code", None)
            else:
                emoji = None
                code = None
            
            if emoji:
                emoji = unicodedata.normalize("NFC", emoji.strip())

            if code:
                code = code.strip().replace(":", "")
                code = f":{code}:"

            ## If we get both let's prioritize only doing the code presuming it's valid
            if await is_valid_code(code):
                await set_cheeremoji_code(env, code)            
            elif await is_valid_emoji(emoji):  ## If not a valid code, then check if it's a valid emoji and do that
                await set_cheeremoji_emoji(env, emoji)
            else:
                console.log(f"BAD POST Path: {url.path}")
                console.log(f"BAD POST Headers: {dict(request.headers)}")
                console.log(f"BAD POST Data: {data}")
                console.log(f"BAD POST Code: {code}")
                console.log(f"BAD POST Emoji: {emoji}")

                return Response.new(json.dumps({"error": "Invalid POST", data: data}), headers=response_headers, status=404)

            ##return await handle_get_cheeremoji(request, env, response_headers)
            return Response.new( json.dumps(await get_cheeremoji(env)), headers=response_headers, status=200)

        else:
            return Response.new(json.dumps("Path Not Found"), headers=response_headers, status=404)

    except Exception as e:
        error_details = traceback.format_exc() # Include the traceback in the response
        return Response.new(json.dumps(f"Error: {str(e)}\n\nDetails:\n{error_details}"), headers=response_headers, status=500)

