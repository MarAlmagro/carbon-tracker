import { test, expect } from '@playwright/test';

/**
 * E2E tests for protected route behavior.
 *
 * Verifies that unauthenticated users are redirected to /signin
 * when accessing protected routes like /profile.
 */

test.describe('Protected Routes', () => {
  test('unauthenticated user visiting /profile is redirected to /signin', async ({ page }) => {
    // Clear any stored auth state
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.removeItem('auth-storage');
    });

    // Navigate to protected route
    await page.goto('/profile');

    // Should be redirected to sign-in
    await expect(page).toHaveURL(/\/signin/, { timeout: 5000 });
  });

  test('unauthenticated user can access /dashboard as guest', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.removeItem('auth-storage');
    });

    await page.goto('/dashboard');

    // Should stay on dashboard (not protected)
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('unauthenticated user can access home page', async ({ page }) => {
    await page.goto('/');
    await page.evaluate(() => {
      localStorage.removeItem('auth-storage');
    });

    await page.goto('/');

    await expect(page).toHaveURL('/');
    await expect(page.getByTestId('nav-signin')).toBeVisible();
  });

  test('continue as guest link from sign-in goes to dashboard', async ({ page }) => {
    await page.goto('/signin');

    await page.getByRole('link', { name: /continue as guest/i }).click();

    await expect(page).toHaveURL(/\/dashboard/);
  });
});
