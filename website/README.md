# BETON Landing Page

This directory is an **isolated static frontend** for the Beton CLI `v0.5.0` release. It has no Python imports, server process, API route, database, or dependency on the CLI package. The Vercel configuration at the repository root runs only this directory’s Vite build and publishes only `website/dist`.

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

The generated `website/dist` directory is the complete Vercel deployment artifact. The deployed landing page links to the versioned documentation at [beton-cli.vercel.app/documentation](https://beton-cli.vercel.app/documentation), with [beton-cli.vercel.app/docs](https://beton-cli.vercel.app/docs) available as an alias.
