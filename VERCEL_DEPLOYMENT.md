# Vercel deployment: frontend only

The repository contains two independent artifacts: the Python CLI in `src/` and the static marketing website in `website/`. Vercel is configured by the root `vercel.json` to install dependencies only within `website/`, run only `website`’s Vite build, and publish only `website/dist`.

> The Python package is neither installed nor run during the Vercel build. It is also not part of the deployed output directory.

## Deploy from GitHub

Import `itsjustayush/beton-cli` into Vercel. Vercel reads the committed `vercel.json` automatically. No root directory change or environment variable is required.

| Vercel setting | Value |
|---|---|
| Install command | `npm --prefix website ci` |
| Build command | `npm --prefix website run build` |
| Output directory | `website/dist` |
| Runtime | Static files only |

## Local verification

```bash
cd website
npm ci
npm run build
```

The result is a static `dist/` directory containing the HTML page and its bundled CSS and JavaScript assets.
