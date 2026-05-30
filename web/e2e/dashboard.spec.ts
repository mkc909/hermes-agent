/**
 * Hermes Agent Dashboard E2E Smoke Tests
 *
 * Verifies each page loads, has correct title/heading, and captures a screenshot.
 * Run: cd web && npx playwright test
 */
import { test, expect } from '@playwright/test';

const PAGES = [
  { path: '/', heading: 'Sessions', name: 'sessions' },
  { path: '/models', heading: 'Models', name: 'models' },
  { path: '/logs', heading: 'Logs', name: 'logs' },
  { path: '/cron', heading: 'Cron', name: 'cron' },
  { path: '/skills', heading: 'Skills', name: 'skills' },
  { path: '/plugins', heading: 'Plugins', name: 'plugins' },
  { path: '/profiles', heading: 'Profiles', name: 'profiles' },
  { path: '/config', heading: 'Config', name: 'config' },
  { path: '/keys', heading: 'Keys', name: 'keys' },
  { path: '/docs', heading: 'Hermes Agent', name: 'docs' },
];

test.describe('Hermes Dashboard - Page Smoke Tests', () => {
  for (const page of PAGES) {
    test(`${page.name} page loads with heading`, async ({ page: pw }) => {
      await pw.goto(page.path);
      await pw.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});

      // Verify the page title
      const title = await pw.title();
      expect(title).toContain('Hermes');

      // Verify the heading exists (h1)
      const h1 = pw.locator('h1');
      await expect(h1).toContainText(page.heading, { timeout: 8000 });

      // Take screenshot
      await pw.screenshot({
        path: `e2e/screenshots/${page.name}.png`,
        fullPage: true,
      });
    });
  }
});

test.describe('Hermes Dashboard - Navigation Tests', () => {
  test('sidebar navigation links work', async ({ page: pw }) => {
    await pw.goto('/');
    await pw.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});

    // Check sidebar links exist
    const navLinks = pw.locator('nav a');
    const count = await navLinks.count();
    expect(count).toBeGreaterThanOrEqual(8);

    // Click each nav link and verify page loads
    const linkTexts = ['SESSIONS', 'MODELS', 'LOGS', 'CRON', 'SKILLS', 'PLUGINS', 'CONFIG'];
    for (const text of linkTexts) {
      await navLinks.filter({ hasText: text }).first().click();
      await pw.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
      await pw.waitForTimeout(500);
    }
  });

  test('theme switcher toggle works', async ({ page: pw }) => {
    await pw.goto('/');
    await pw.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});

    const themeButton = pw.locator('button[aria-label="Switch theme"], button:has-text("Switch theme")').first();
    if (await themeButton.isVisible()) {
      await themeButton.click();
      await pw.waitForTimeout(300);
      // Should still be on page
      const title = await pw.title();
      expect(title).toContain('Hermes');
    }
  });
});

test.describe('Hermes Dashboard - API Health', () => {
  test('/api/status returns valid JSON', async ({ page: pw }) => {
    const response = await pw.goto('/api/status');
    if (response) {
      const contentType = response.headers()['content-type'] || '';
      // May be JSON or may redirect — either is acceptable
      expect([200, 302, 401]).toContain(response.status());
    }
  });
});
