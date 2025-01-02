## Cloudflare Workers

  * Wrangler Commands: https://developers.cloudflare.com/workers/wrangler/commands/
  * Wrangler Config: https://developers.cloudflare.com/workers/wrangler/configuration/
  * Local Dev: https://developers.cloudflare.com/workers/testing/local-development/
  * Python Dev: https://developers.cloudflare.com/workers/languages/python/
    - Examples: https://github.com/cloudflare/python-workers-examples
  * Quickstarts: https://developers.cloudflare.com/workers/get-started/quickstarts/

## Check
  * https://developers.cloudflare.com/pages/get-started/c3/#creating-a-new-pages-project-that-is-connected-to-a-git-repository



## Future
  * Emoji package: https://pypi.org/project/emoji/
  * Websockets: https://developers.cloudflare.com/workers/runtime-apis/websockets/
    - Hibernate: https://developers.cloudflare.com/durable-objects/best-practices/websockets/#websocket-hibernation-api

## Creation

`npm create cloudflare@latest -y -- --type hello-world-python --lang python -- telemetry disable`

## In Prod

`To have wrangler dev connect to your Workers KV namespace running on Cloudflare's global network, call wrangler dev --remote instead. This will use the preview_id of the KV binding configuration in the wrangler.toml file. This is how a wrangler.toml file looks with the preview_id specified.` - https://developers.cloudflare.com/kv/concepts/kv-bindings/#use-kv-bindings-when-developing-locally

Routing

```Set up a route in the dashboard
Before you set up a route, make sure you have a DNS record set up for the domain or subdomain you would like to route to.
To set up a route in the dashboard:
Log in to the Cloudflare dashboard ↗ and select your account.
Go to Workers & Pages and in Overview, select your Worker.
Go to Settings > Triggers > Routes > Add route.
Enter the route and select the zone it applies to.
Select Add route.```

- https://developers.cloudflare.com/workers/configuration/routing/routes/#set-up-a-route-in-the-dashboard
