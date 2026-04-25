/// <reference types="vitest" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": "http://localhost:8000",
    },
  },
  test: {
    globals: true,                  // <-- ADDED: Makes describe, test, and expect global
    setupFiles: "./tests/setup.ts", // <-- ADDED: Automatically injects jest-dom matchers
    include: ["tests/web/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
    environment: "happy-dom",
  },
});