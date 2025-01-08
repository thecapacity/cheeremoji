# cheeremoji
Global Cheer Emoji site - cheeremoji.com

Built using Cloudflare Pages and their (beta) pythn workers. It's a tad 'incomplekte', e.g. I'd love to do Websockets but still puzzling through the sparse documentation.

### Layout and Launch
- Primsry pages are in the root directory. The worker itself resides in `src/` but the `worker.toml` for configuration is in `/`.
- Run locally with `npx wrangler dev --log-level info`

Note, some debugging messaging is inconsistent and/or I couldn't figure out (e.g. the python logging didn't really work and you sometimes have to consider converting objects from JS to Python before printing). It's definitely a flashback to more retro debugging methods, e.g. `print("1")`

### Workflow

- `main` is for local development
- `publish` gets pushed to Cloudflare via a GitHub Action [deployment script](https://github.com/thecapacity/cheeremoji/blob/main/.github/workflows/deploy.yaml)


#### Misc
- `noted.md` maintained some working notes / references as I developed - may still be useful to some
