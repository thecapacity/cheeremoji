# cheeremoji
Global Cheer Emoji site - cheeremoji.com

Built using Cloudflare Pages and their (beta) pythn workers. It's a tad 'incomplekte', e.g. I'd love to do Websockets but still puzzling through the sparse documentation.

### Workflow

- `main` is for local development
- `publish` gets pushed to Cloudflare via a GitHub Action [deployment script](https://github.com/thecapacity/cheeremoji/blob/main/.github/workflows/deploy.yaml)
