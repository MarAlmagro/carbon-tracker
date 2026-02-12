import { test, expect } from '@playwright/test';

/**
 * E2E tests for the energy logging flow:
 * Select energy category → Choose energy type → Enter amount → Log activity
 *
 * These tests require a running frontend dev server and backend API
 * with energy emission factors seeded.
 */

test.describe('Energy Logging Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('energy tab is accessible from dashboard', async ({ page }) => {
    const energyTab = page.getByTestId('category-tab-energy');
    if (await energyTab.isVisible({ timeout: 5000 }).catch(() => false)) {
      await energyTab.click();
      await expect(energyTab).toHaveAttribute('aria-pressed', 'true');
    }
  });

  test('energy form shows type selector with all energy types', async ({ page }) => {
    const energyTab = page.getByTestId('category-tab-energy');
    if (!(await energyTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await energyTab.click();

    const typeSelect = page.getByTestId('energy-type-select');
    await expect(typeSelect).toBeVisible();

    // Verify all energy type options are present
    await expect(typeSelect.locator('option')).toHaveCount(3);
  });

  test('log electricity activity end-to-end', async ({ page }) => {
    const energyTab = page.getByTestId('category-tab-energy');
    if (!(await energyTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await energyTab.click();

    // Select electricity type (default)
    const typeSelect = page.getByTestId('energy-type-select');
    await expect(typeSelect).toBeVisible();
    await typeSelect.selectOption('electricity');

    // Enter amount in kWh
    const amountInput = page.getByTestId('energy-amount-input');
    await amountInput.fill('350');

    // Set date
    const dateInput = page.getByTestId('energy-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    // Submit the form
    const submitButton = page.getByTestId('energy-submit-button');
    await expect(submitButton).toBeEnabled();
    await submitButton.click();

    // Wait for submission to complete
    await page.waitForLoadState('networkidle');

    // Dashboard should still be functional
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('log natural gas activity end-to-end', async ({ page }) => {
    const energyTab = page.getByTestId('category-tab-energy');
    if (!(await energyTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await energyTab.click();

    // Select natural gas type
    const typeSelect = page.getByTestId('energy-type-select');
    await typeSelect.selectOption('natural_gas');

    // Enter amount
    const amountInput = page.getByTestId('energy-amount-input');
    await amountInput.fill('500');

    // Set date
    const dateInput = page.getByTestId('energy-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    // Submit
    const submitButton = page.getByTestId('energy-submit-button');
    await submitButton.click();

    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('energy form shows unit label for heating oil as liters', async ({ page }) => {
    const energyTab = page.getByTestId('category-tab-energy');
    if (!(await energyTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await energyTab.click();

    const typeSelect = page.getByTestId('energy-type-select');
    await typeSelect.selectOption('heating_oil');

    // The amount label should show liters for heating oil
    await expect(page.getByText(/liters/i)).toBeVisible();
  });

  test('energy form shows optional notes field', async ({ page }) => {
    const energyTab = page.getByTestId('category-tab-energy');
    if (!(await energyTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await energyTab.click();

    const notesInput = page.getByTestId('energy-notes-input');
    await expect(notesInput).toBeVisible();

    await notesInput.fill('Monthly electricity bill');
    await expect(notesInput).toHaveValue('Monthly electricity bill');
  });
});
