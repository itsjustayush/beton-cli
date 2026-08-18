# BETON Landing Page

This directory is an **isolated static frontend**. It has no Python imports, server process, API route, database, or dependency on the CLI package. The Vercel configuration at the repository root runs only this directory’s Vite build and publishes only `website/dist`.

## Local preview

```bash
cd website
npm install
npm run dev
```

## Production build

```bash
cd website
npm run build
```

The generated `website/dist` directory is the complete Vercel deployment artifact.
