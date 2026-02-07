import { test, expect } from '@playwright/test'

test('homepage shows Hello World', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.app')).toHaveText('Hello World')
})


test('backend /api/hello returns expected JSON', async ({ request }) => {
  const res = await request.get('http://localhost:5000/api/hello')
  expect(res.ok()).toBeTruthy()
  const json = await res.json()
  expect(json).toEqual({ message: 'Hello from Fastify' })
})
