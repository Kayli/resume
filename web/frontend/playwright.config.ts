import { defineConfig, devices } from '@playwright/test'
import { resolve } from 'path'

// Ensure Playwright looks for browsers in the global image cache path when running tests
process.env.PLAYWRIGHT_BROWSERS_PATH = process.env.PLAYWRIGHT_BROWSERS_PATH || '/ms-playwright'

export default defineConfig({
  testDir: './tests',
  timeout: 30_000,
  expect: { timeout: 5_000 },
  fullyParallel: true,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:3000',
    headless: true,
    screenshot: 'only-on-failure'
  },
  webServer: {
    // start both frontend and backend together (frontend's `dev` script runs concurrently)
    command: 'npm run dev',
    cwd: resolve(__dirname),
    url: 'http://localhost:3000',
    reuseExistingServer: false,
    timeout: 180_000
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ]
})
