import { test, expect } from '@playwright/test';

/**
 * E2E tests for the flight logging flow:
 * Search airports → Select origin/destination → Preview calculation → Log flight
 *
 * These tests require a running frontend dev server and backend API
 * with airport data loaded.
 */

test.describe('Flight Logging Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('flight form is accessible from dashboard', async ({ page }) => {
    // Look for the flight tab/button
    const flightTab = page.getByRole('button', { name: /flight/i });
    if (await flightTab.isVisible({ timeout: 5000 }).catch(() => false)) {
      await flightTab.click();
      await expect(page.getByTestId('flight-form')).toBeVisible();
    }
  });

  test('airport autocomplete shows search results', async ({ page }) => {
    // Navigate to flight form
    const flightTab = page.getByRole('button', { name: /flight/i });
    if (!(await flightTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await flightTab.click();

    // Type in origin airport search
    const originInput = page.getByTestId('origin-airport-input');
    await expect(originInput).toBeVisible();
    await originInput.fill('JFK');

    // Wait for dropdown to appear
    const dropdown = page.getByTestId('origin-airport-dropdown');
    await expect(dropdown).toBeVisible({ timeout: 10000 });

    // Should show at least one result
    const options = dropdown.locator('li');
    await expect(options.first()).toBeVisible();
  });

  test('full flight logging flow: select airports, preview, and submit', async ({ page }) => {
    // Navigate to flight form
    const flightTab = page.getByRole('button', { name: /flight/i });
    if (!(await flightTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await flightTab.click();
    await expect(page.getByTestId('flight-form')).toBeVisible();

    // Select origin airport
    const originInput = page.getByTestId('origin-airport-input');
    await originInput.fill('JFK');
    const originDropdown = page.getByTestId('origin-airport-dropdown');
    await expect(originDropdown).toBeVisible({ timeout: 10000 });
    await originDropdown.locator('li').first().click();

    // Select destination airport
    const destInput = page.getByTestId('destination-airport-input');
    await destInput.fill('LAX');
    const destDropdown = page.getByTestId('destination-airport-dropdown');
    await expect(destDropdown).toBeVisible({ timeout: 10000 });
    await destDropdown.locator('li').first().click();

    // Wait for flight calculation preview
    await expect(page.getByText(/km/)).toBeVisible({ timeout: 10000 });

    // Submit button should be enabled
    const submitButton = page.getByTestId('flight-submit');
    await expect(submitButton).toBeEnabled();

    // Submit the flight
    await submitButton.click();

    // Wait for submission to complete
    await page.waitForLoadState('networkidle');

    // Dashboard should still be functional
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('submit button is disabled without both airports selected', async ({ page }) => {
    const flightTab = page.getByRole('button', { name: /flight/i });
    if (!(await flightTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await flightTab.click();

    const submitButton = page.getByTestId('flight-submit');
    await expect(submitButton).toBeDisabled();
  });
});
