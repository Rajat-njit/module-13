import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/e2e',
  timeout: 30000,
  use: {
    headless: true,
    baseURL: 'http://127.0.0.1:8000',
  },
  webServer: {
    command: 'uvicorn app.main:app --host 0.0.0.0 --port 8000',
    port: 8000,
    timeout: 20000,
    reuseExistingServer: !process.env.CI,
  },
});
