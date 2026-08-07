import { defineConfig } from "astro/config";
import react from "@astrojs/react";

export default defineConfig({
  integrations: [react()],
  server: {
    proxy: {
      "/v1": "http://localhost:8000",
      "/login_user": "http://localhost:8000",
    },
  },
});
