import { test, expect } from '@playwright/test';

/**
 * E2E tests for the full authentication flow:
 * Sign Up → Sign In → View Profile → Sign Out
 *
 * These tests require a running frontend dev server and a configured
 * Supabase instance. Set VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY
 * in a .env file before running.
 */

const TEST_EMAIL = `e2e-${Date.now()}@test.example.com`;
const TEST_PASSWORD = 'TestPassword123!';

test.describe('Authentication Flow', () => {
  test('full sign-up → sign-in → profile → sign-out flow', async ({ page }) => {
    // 1. Navigate to sign-up page
    await page.goto('/signup');
    await expect(page.getByTestId('signup-form')).toBeVisible();

    // 2. Fill in sign-up form
    await page.getByTestId('email-input').fill(TEST_EMAIL);
    await page.getByTestId('password-input').fill(TEST_PASSWORD);
    await page.getByTestId('confirm-password-input').fill(TEST_PASSWORD);
    await page.getByTestId('terms-checkbox').check();

    // 3. Submit sign-up
    await page.getByTestId('signup-button').click();

    // 4. Should redirect to dashboard after sign-up
    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });

    // 5. Navigate to profile
    await page.getByTestId('nav-profile').click();
    await expect(page).toHaveURL(/\/profile/);

    // 6. Verify profile displays email
    await expect(page.getByTestId('profile-email')).toContainText(TEST_EMAIL);
    await expect(page.getByTestId('profile-created-at')).toBeVisible();

    // 7. Sign out
    await page.getByTestId('signout-button').click();

    // 8. Should redirect to home
    await expect(page).toHaveURL('/');

    // 9. Navigation should show Sign In link
    await expect(page.getByTestId('nav-signin')).toBeVisible();
  });

  test('sign-in with valid credentials', async ({ page }) => {
    await page.goto('/signin');
    await expect(page.getByTestId('signin-form')).toBeVisible();

    await page.getByTestId('email-input').fill(TEST_EMAIL);
    await page.getByTestId('password-input').fill(TEST_PASSWORD);
    await page.getByTestId('signin-button').click();

    await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
    await expect(page.getByTestId('nav-profile')).toBeVisible();
  });

  test('sign-in with invalid credentials shows error', async ({ page }) => {
    await page.goto('/signin');

    await page.getByTestId('email-input').fill('nonexistent@test.com');
    await page.getByTestId('password-input').fill('wrongpassword');
    await page.getByTestId('signin-button').click();

    await expect(page.getByRole('alert')).toBeVisible({ timeout: 5000 });
  });

  test('sign-in page has links to sign-up and guest mode', async ({ page }) => {
    await page.goto('/signin');

    await expect(page.getByRole('link', { name: /sign up/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /continue as guest/i })).toBeVisible();
    await expect(page.getByRole('link', { name: /forgot password/i })).toBeVisible();
  });

  test('sign-up page validates password match', async ({ page }) => {
    await page.goto('/signup');

    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('different');

    await expect(page.getByText(/passwords do not match/i)).toBeVisible();
  });
});
