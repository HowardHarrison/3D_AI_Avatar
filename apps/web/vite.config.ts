import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

/**
 * Vite configuration for the presenter SPA.
 * Host binding is required so Docker port mapping can reach the dev server.
 */
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@avatar/shared": path.resolve(__dirname, "../../packages/shared/src/index.ts"),
    },
  },
  server: {
    host: true,
    port: 5173,
  },
  preview: {
    host: true,
    port: 4173,
  },
});
