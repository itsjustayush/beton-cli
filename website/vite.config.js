// The website is intentionally an isolated static build. Vercel serves only website/dist.
import { defineConfig } from "vite";

import { resolve } from "node:path";

export default defineConfig({
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        home: resolve(__dirname, "index.html"),
        docs: resolve(__dirname, "documentation.html"),
        docsAlias: resolve(__dirname, "docs.html"),
      },
    },
  },
  server: { allowedHosts: true },
});
