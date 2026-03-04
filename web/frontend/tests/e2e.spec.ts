import { test, expect } from '@playwright/test'

test('homepage shows resume header', async ({ page }) => {
  await page.goto('/')
  await expect(page.locator('.resume-header h1')).toHaveText('Illia Karpenkov')
})


test('backend /api/resume returns resume JSON', async ({ request }) => {
  const res = await request.get('http://localhost:5000/api/resume')
  expect(res.ok()).toBeTruthy()
  const json = await res.json()
  expect(json).toHaveProperty('header')
  expect(json.header).toHaveProperty('name', 'Illia Karpenkov')
  expect(Array.isArray(json.roles)).toBeTruthy()
  expect(json.roles.length).toBeGreaterThan(0)
})
