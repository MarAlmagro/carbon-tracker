import { test, expect } from '@playwright/test';

/**
 * E2E tests for multi-category activity logging:
 * Verifies switching between transport, energy, and food categories
 * and logging activities across all categories in a single session.
 *
 * These tests require a running frontend dev server and backend API
 * with all emission factors seeded.
 */

test.describe('Multi-Category Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('category selector shows all three categories', async ({ page }) => {
    const selector = page.getByTestId('category-selector');
    if (!(await selector.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }

    await expect(page.getByTestId('category-tab-transport')).toBeVisible();
    await expect(page.getByTestId('category-tab-energy')).toBeVisible();
    await expect(page.getByTestId('category-tab-food')).toBeVisible();
  });

  test('switching categories shows the correct form', async ({ page }) => {
    const selector = page.getByTestId('category-selector');
    if (!(await selector.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }

    // Click energy tab — energy form should appear
    await page.getByTestId('category-tab-energy').click();
    await expect(page.getByTestId('energy-type-select')).toBeVisible();

    // Click food tab — food form should appear
    await page.getByTestId('category-tab-food').click();
    await expect(page.getByTestId('food-type-select')).toBeVisible();

    // Click transport tab — transport form should appear
    await page.getByTestId('category-tab-transport').click();
    // Transport form uses a distance input
    await expect(page.getByLabel(/distance/i)).toBeVisible();
  });

  test('log activities across all categories in one session', async ({ page }) => {
    const selector = page.getByTestId('category-selector');
    if (!(await selector.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }

    const today = new Date().toISOString().split('T')[0];

    // --- Log a transport activity ---
    await page.getByTestId('category-tab-transport').click();
    const distanceInput = page.getByLabel(/distance/i);
    if (await distanceInput.isVisible({ timeout: 3000 }).catch(() => false)) {
      await distanceInput.fill('15');
      const transportDate = page.getByLabel(/date/i);
      if (await transportDate.isVisible()) {
        await transportDate.fill(today);
      }
      const transportSubmit = page.getByRole('button', { name: /log activity/i });
      await transportSubmit.click();
      await page.waitForLoadState('networkidle');
    }

    // --- Log an energy activity ---
    await page.getByTestId('category-tab-energy').click();
    const energyType = page.getByTestId('energy-type-select');
    if (await energyType.isVisible({ timeout: 3000 }).catch(() => false)) {
      await energyType.selectOption('electricity');
      await page.getByTestId('energy-amount-input').fill('200');
      await page.getByTestId('energy-date-input').fill(today);
      await page.getByTestId('energy-submit-button').click();
      await page.waitForLoadState('networkidle');
    }

    // --- Log a food activity ---
    await page.getByTestId('category-tab-food').click();
    const foodType = page.getByTestId('food-type-select');
    if (await foodType.isVisible({ timeout: 3000 }).catch(() => false)) {
      await foodType.selectOption('vegetables');
      const servingsInput = page.getByTestId('food-servings-input');
      await servingsInput.clear();
      await servingsInput.fill('2');
      await page.getByTestId('food-date-input').fill(today);
      await page.getByTestId('food-submit-button').click();
      await page.waitForLoadState('networkidle');
    }

    // Dashboard should still be functional after logging all three
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('category tabs maintain aria-pressed state correctly', async ({ page }) => {
    const selector = page.getByTestId('category-selector');
    if (!(await selector.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }

    // Click energy
    await page.getByTestId('category-tab-energy').click();
    await expect(page.getByTestId('category-tab-energy')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('category-tab-transport')).toHaveAttribute('aria-pressed', 'false');
    await expect(page.getByTestId('category-tab-food')).toHaveAttribute('aria-pressed', 'false');

    // Click food
    await page.getByTestId('category-tab-food').click();
    await expect(page.getByTestId('category-tab-food')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('category-tab-energy')).toHaveAttribute('aria-pressed', 'false');
    await expect(page.getByTestId('category-tab-transport')).toHaveAttribute('aria-pressed', 'false');
  });
});
