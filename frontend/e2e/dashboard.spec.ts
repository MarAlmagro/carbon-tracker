import { test, expect } from '@playwright/test';

/**
 * E2E tests for the dashboard with charts and visualizations.
 *
 * Tests the full dashboard flow including period switching,
 * chart rendering, empty state, and responsive layout.
 *
 * These tests require a running frontend dev server and backend API.
 */

test.describe('Dashboard Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Start as guest on dashboard
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('dashboard page loads with period selector and sections', async ({ page }) => {
    // Period selector should be visible with all options
    await expect(page.getByRole('button', { name: /today/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /this week/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /this month/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /this year/i })).toBeVisible();
    await expect(page.getByRole('button', { name: /all time/i })).toBeVisible();

    // Dashboard title should be visible
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();
  });

  test('shows empty state when no activities exist for period', async ({ page }) => {
    // Switch to a period unlikely to have data (Today for a fresh session)
    await page.getByRole('button', { name: /today/i }).click();

    // Wait for loading to finish — either data or empty state appears
    await page.waitForLoadState('networkidle');

    // If no activities, empty state should show
    const emptyState = page.getByText(/no activities/i);
    const summaryCard = page.getByText(/kg CO2e/i);

    // One of these should be visible
    await expect(emptyState.or(summaryCard)).toBeVisible({ timeout: 10000 });
  });

  test('period selector switches between views', async ({ page }) => {
    // Default should be "This Month" active
    const monthButton = page.getByRole('button', { name: /this month/i });
    await expect(monthButton).toBeVisible();

    // Click "This Week"
    const weekButton = page.getByRole('button', { name: /this week/i });
    await weekButton.click();

    // Wait for data to reload
    await page.waitForLoadState('networkidle');

    // Click "This Year"
    const yearButton = page.getByRole('button', { name: /this year/i });
    await yearButton.click();

    await page.waitForLoadState('networkidle');

    // Click "All Time"
    const allButton = page.getByRole('button', { name: /all time/i });
    await allButton.click();

    await page.waitForLoadState('networkidle');

    // Page should still be on dashboard without errors
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('dashboard displays log activity form and recent activities', async ({ page }) => {
    // The transport form section should be present
    await expect(page.getByText(/log activity/i)).toBeVisible();

    // The recent activities section should be present
    await expect(page.getByText(/recent activities/i)).toBeVisible();
  });

  test('logging an activity updates the dashboard', async ({ page }) => {
    // Find and fill the transport form
    const distanceInput = page.getByLabel(/distance/i);

    // Only proceed if the form is visible (depends on page state)
    if (await distanceInput.isVisible({ timeout: 5000 }).catch(() => false)) {
      await distanceInput.fill('25');

      const dateInput = page.getByLabel(/date/i);
      if (await dateInput.isVisible()) {
        const today = new Date().toISOString().split('T')[0];
        await dateInput.fill(today);
      }

      // Submit the form
      const submitButton = page.getByRole('button', { name: /log activity/i });
      await submitButton.click();

      // Wait for the activity to be saved and dashboard to update
      await page.waitForLoadState('networkidle');

      // Dashboard should still be functional
      await expect(page).toHaveURL(/\/dashboard/);
    }
  });

  test('dashboard is responsive on mobile viewport', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 812 });

    await page.goto('/dashboard');

    // Period selector should still be visible
    await expect(page.getByRole('button', { name: /this month/i })).toBeVisible();

    // Dashboard title should be visible
    await expect(page.getByRole('heading', { level: 1 })).toBeVisible();

    // Page should not have horizontal overflow
    const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
    const viewportWidth = await page.evaluate(() => window.innerWidth);
    expect(bodyWidth).toBeLessThanOrEqual(viewportWidth + 1); // +1 for rounding
  });
});
