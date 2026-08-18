// The website is intentionally an isolated static build. Vercel serves only website/dist.
import { defineConfig } from "vite";

export default defineConfig({
  build: { outDir: "dist", emptyOutDir: true },
  server: { allowedHosts: true },
});
