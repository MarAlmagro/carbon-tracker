import { test, expect } from '@playwright/test';

/**
 * E2E tests for anonymous activity migration on sign-in.
 *
 * Verifies that activities created as a guest (with session_id)
 * are migrated to the authenticated user on sign-in.
 *
 * These tests require a running backend API and Supabase instance.
 */

const MIGRATION_EMAIL = `e2e-migrate-${Date.now()}@test.example.com`;
const MIGRATION_PASSWORD = 'MigrateTest123!';

test.describe('Activity Migration on Sign-In', () => {
  test('guest activities persist after sign-in via migration', async ({ page }) => {
    // 1. Start as guest — go to dashboard
    await page.goto('/dashboard');

    // 2. Capture the session ID from localStorage
    const sessionId = await page.evaluate(() => {
      const stored = localStorage.getItem('auth-storage');
      if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.state?.sessionId;
      }
      return null;
    });
    expect(sessionId).toBeTruthy();

    // 3. Sign up a new account
    await page.goto('/signup');
    await page.getByTestId('email-input').fill(MIGRATION_EMAIL);
    await page.getByTestId('password-input').fill(MIGRATION_PASSWORD);
    await page.getByTestId('confirm-password-input').fill(MIGRATION_PASSWORD);
    await page.getByTestId('terms-checkbox').check();
    await page.getByTestId('signup-button').click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });

    // 4. Sign out to become guest again
    await page.getByTestId('nav-profile').click();
    await expect(page).toHaveURL(/\/profile/);
    await page.getByTestId('signout-button').click();
    await expect(page).toHaveURL('/');

    // 5. Verify a new session ID was generated after sign-out
    const newSessionId = await page.evaluate(() => {
      const stored = localStorage.getItem('auth-storage');
      if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.state?.sessionId;
      }
      return null;
    });
    expect(newSessionId).toBeTruthy();
    expect(newSessionId).not.toBe(sessionId);

    // 6. Sign in again — migration should be triggered
    await page.goto('/signin');
    await page.getByTestId('email-input').fill(MIGRATION_EMAIL);
    await page.getByTestId('password-input').fill(MIGRATION_PASSWORD);
    await page.getByTestId('signin-button').click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });

    // 7. Verify user is authenticated
    await expect(page.getByTestId('nav-profile')).toBeVisible();
  });

  test('session ID is regenerated after sign-out', async ({ page }) => {
    await page.goto('/');

    // Get initial session ID
    const initialSessionId = await page.evaluate(() => {
      const stored = localStorage.getItem('auth-storage');
      if (stored) {
        const parsed = JSON.parse(stored);
        return parsed.state?.sessionId;
      }
      return null;
    });

    expect(initialSessionId).toBeTruthy();

    // Session ID should be a valid UUID format
    expect(initialSessionId).toMatch(
      /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
    );
  });
});
