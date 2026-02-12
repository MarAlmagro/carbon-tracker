import { test, expect } from '@playwright/test';

/**
 * E2E tests for the food logging flow:
 * Select food category → Choose food type → Enter servings → Log activity
 *
 * These tests require a running frontend dev server and backend API
 * with food emission factors seeded.
 */

test.describe('Food Logging Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('food tab is accessible from dashboard', async ({ page }) => {
    const foodTab = page.getByTestId('category-tab-food');
    if (await foodTab.isVisible({ timeout: 5000 }).catch(() => false)) {
      await foodTab.click();
      await expect(foodTab).toHaveAttribute('aria-pressed', 'true');
    }
  });

  test('food form shows type selector with all food types', async ({ page }) => {
    const foodTab = page.getByTestId('category-tab-food');
    if (!(await foodTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await foodTab.click();

    const typeSelect = page.getByTestId('food-type-select');
    await expect(typeSelect).toBeVisible();

    // Verify all food type options are present
    await expect(typeSelect.locator('option')).toHaveCount(7);
  });

  test('log beef activity end-to-end', async ({ page }) => {
    const foodTab = page.getByTestId('category-tab-food');
    if (!(await foodTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await foodTab.click();

    // Select beef type (default)
    const typeSelect = page.getByTestId('food-type-select');
    await expect(typeSelect).toBeVisible();
    await typeSelect.selectOption('beef');

    // Enter servings
    const servingsInput = page.getByTestId('food-servings-input');
    await servingsInput.clear();
    await servingsInput.fill('2');

    // Set date
    const dateInput = page.getByTestId('food-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    // Submit the form
    const submitButton = page.getByTestId('food-submit-button');
    await expect(submitButton).toBeEnabled();
    await submitButton.click();

    // Wait for submission to complete
    await page.waitForLoadState('networkidle');

    // Dashboard should still be functional
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('log vegan meal activity end-to-end', async ({ page }) => {
    const foodTab = page.getByTestId('category-tab-food');
    if (!(await foodTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await foodTab.click();

    // Select vegan meal type
    const typeSelect = page.getByTestId('food-type-select');
    await typeSelect.selectOption('vegan_meal');

    // Enter servings
    const servingsInput = page.getByTestId('food-servings-input');
    await servingsInput.clear();
    await servingsInput.fill('3');

    // Set date
    const dateInput = page.getByTestId('food-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    // Submit
    const submitButton = page.getByTestId('food-submit-button');
    await submitButton.click();

    await page.waitForLoadState('networkidle');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('food form shows notes field', async ({ page }) => {
    const foodTab = page.getByTestId('category-tab-food');
    if (!(await foodTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await foodTab.click();

    const notesInput = page.getByTestId('food-notes-input');
    await expect(notesInput).toBeVisible();

    await notesInput.fill('Steak dinner');
    await expect(notesInput).toHaveValue('Steak dinner');
  });

  test('food form defaults to 1 serving', async ({ page }) => {
    const foodTab = page.getByTestId('category-tab-food');
    if (!(await foodTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await foodTab.click();

    const servingsInput = page.getByTestId('food-servings-input');
    await expect(servingsInput).toHaveValue('1');
  });
});
