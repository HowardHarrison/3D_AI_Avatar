import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "node:path";

/**
 * Vitest uses the same aliases as Vite so unit tests can import @avatar/shared.
 */
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@avatar/shared": path.resolve(__dirname, "../../packages/shared/src/index.ts"),
    },
  },
  test: {
    environment: "node",
    include: ["src/**/*.test.ts"],
  },
});
