import { test, expect } from '@playwright/test';

/**
 * E2E tests for activity management (edit/delete) flow:
 * Create activity → Edit activity → Delete activity with confirmation
 *
 * These tests require a running frontend dev server and backend API.
 */

test.describe('Activity Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard/);
  });

  test('create, edit, and delete transport activity', async ({ page }) => {
    // Step 1: Create an activity first
    const transportTab = page.getByTestId('category-tab-transport');
    if (!(await transportTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await transportTab.click();

    // Select bus type
    const typeSelect = page.getByTestId('transport-type-select');
    await expect(typeSelect).toBeVisible();
    await typeSelect.selectOption('bus');

    // Enter distance
    const distanceInput = page.getByTestId('transport-distance-input');
    await distanceInput.fill('25');

    // Set date
    const dateInput = page.getByTestId('transport-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    // Add notes
    const notesInput = page.getByTestId('transport-notes-input');
    await notesInput.fill('Original commute');

    // Submit form
    const submitButton = page.getByTestId('log-transport-button');
    await submitButton.click();

    // Wait for activity to appear in the list
    await expect(page.getByText(/25 km/)).toBeVisible({ timeout: 10000 });
    await expect(page.getByText(/Original commute/)).toBeVisible();

    // Step 2: Edit the activity
    const editButton = page.getByTestId('edit-activity-button').first();
    await expect(editButton).toBeVisible();
    await editButton.click();

    // Wait for edit modal to open
    await expect(page.getByText('Edit Activity')).toBeVisible();

    // Change value
    const editValueInput = page.getByTestId('edit-value-input');
    await editValueInput.clear();
    await editValueInput.fill('30');

    // Change notes
    const editNotesInput = page.getByTestId('edit-notes-input');
    await editNotesInput.clear();
    await editNotesInput.fill('Updated commute distance');

    // Verify CO2e preview is shown
    await expect(page.getByText(/New CO2e:/)).toBeVisible();

    // Save changes
    const saveButton = page.getByTestId('save-changes-button');
    await saveButton.click();

    // Wait for modal to close and verify updated activity
    await expect(page.getByText('Edit Activity')).not.toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/30 km/)).toBeVisible();
    await expect(page.getByText(/Updated commute distance/)).toBeVisible();

    // Step 3: Delete the activity
    const deleteButton = page.getByTestId('delete-activity-button').first();
    await expect(deleteButton).toBeVisible();
    await deleteButton.click();

    // Wait for delete confirmation dialog
    await expect(page.getByText('Delete Activity?')).toBeVisible();
    await expect(page.getByText(/This cannot be undone/)).toBeVisible();

    // Verify activity summary is shown in dialog
    await expect(page.getByText(/30 km/)).toBeVisible();

    // Confirm deletion
    const confirmDeleteButton = page.getByTestId('confirm-delete-button');
    await confirmDeleteButton.click();

    // Wait for dialog to close and activity to be removed
    await expect(page.getByText('Delete Activity?')).not.toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/Updated commute distance/)).not.toBeVisible();
  });

  test('cancel edit modal without saving changes', async ({ page }) => {
    // Create an activity first
    const transportTab = page.getByTestId('category-tab-transport');
    if (!(await transportTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await transportTab.click();

    const typeSelect = page.getByTestId('transport-type-select');
    await typeSelect.selectOption('car_petrol');

    const distanceInput = page.getByTestId('transport-distance-input');
    await distanceInput.fill('20');

    const dateInput = page.getByTestId('transport-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    const submitButton = page.getByTestId('log-transport-button');
    await submitButton.click();

    await expect(page.getByText(/20 km/)).toBeVisible({ timeout: 10000 });

    // Open edit modal
    const editButton = page.getByTestId('edit-activity-button').first();
    await editButton.click();
    await expect(page.getByText('Edit Activity')).toBeVisible();

    // Make changes but cancel
    const editValueInput = page.getByTestId('edit-value-input');
    await editValueInput.clear();
    await editValueInput.fill('50');

    const cancelButton = page.getByRole('button', { name: /cancel/i });
    await cancelButton.click();

    // Verify modal closed and original value is still shown
    await expect(page.getByText('Edit Activity')).not.toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/20 km/)).toBeVisible();
    await expect(page.getByText(/50 km/)).not.toBeVisible();
  });

  test('cancel delete dialog without deleting', async ({ page }) => {
    // Create an activity first
    const transportTab = page.getByTestId('category-tab-transport');
    if (!(await transportTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await transportTab.click();

    const typeSelect = page.getByTestId('transport-type-select');
    await typeSelect.selectOption('train');

    const distanceInput = page.getByTestId('transport-distance-input');
    await distanceInput.fill('100');

    const dateInput = page.getByTestId('transport-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    const submitButton = page.getByTestId('log-transport-button');
    await submitButton.click();

    await expect(page.getByText(/100 km/)).toBeVisible({ timeout: 10000 });

    // Open delete dialog
    const deleteButton = page.getByTestId('delete-activity-button').first();
    await deleteButton.click();
    await expect(page.getByText('Delete Activity?')).toBeVisible();

    // Cancel deletion
    const cancelButton = page.getByRole('button', { name: /cancel/i });
    await cancelButton.click();

    // Verify dialog closed and activity is still present
    await expect(page.getByText('Delete Activity?')).not.toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/100 km/)).toBeVisible();
  });

  test('edit activity updates CO2e value', async ({ page }) => {
    // Create activity
    const transportTab = page.getByTestId('category-tab-transport');
    if (!(await transportTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await transportTab.click();

    const typeSelect = page.getByTestId('transport-type-select');
    await typeSelect.selectOption('car_petrol');

    const distanceInput = page.getByTestId('transport-distance-input');
    await distanceInput.fill('100');

    const dateInput = page.getByTestId('transport-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    const submitButton = page.getByTestId('log-transport-button');
    await submitButton.click();

    await expect(page.getByText(/100 km/)).toBeVisible({ timeout: 10000 });

    // Get initial CO2e value
    const initialCo2e = await page.getByText(/kg CO2e/).first().textContent();

    // Edit activity to change distance
    const editButton = page.getByTestId('edit-activity-button').first();
    await editButton.click();

    const editValueInput = page.getByTestId('edit-value-input');
    await editValueInput.clear();
    await editValueInput.fill('200');

    const saveButton = page.getByTestId('save-changes-button');
    await saveButton.click();

    await expect(page.getByText('Edit Activity')).not.toBeVisible({ timeout: 5000 });

    // Get updated CO2e value
    const updatedCo2e = await page.getByText(/kg CO2e/).first().textContent();

    // Verify CO2e changed (should be approximately doubled)
    expect(initialCo2e).not.toBe(updatedCo2e);
    await expect(page.getByText(/200 km/)).toBeVisible();
  });

  test('edit modal pre-fills with current activity data', async ({ page }) => {
    // Create activity with specific values
    const transportTab = page.getByTestId('category-tab-transport');
    if (!(await transportTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await transportTab.click();

    const typeSelect = page.getByTestId('transport-type-select');
    await typeSelect.selectOption('bike');

    const distanceInput = page.getByTestId('transport-distance-input');
    await distanceInput.fill('15');

    const dateInput = page.getByTestId('transport-date-input');
    const testDate = '2026-02-10';
    await dateInput.fill(testDate);

    const notesInput = page.getByTestId('transport-notes-input');
    await notesInput.fill('Bike to work');

    const submitButton = page.getByTestId('log-transport-button');
    await submitButton.click();

    await expect(page.getByText(/15 km/)).toBeVisible({ timeout: 10000 });

    // Open edit modal
    const editButton = page.getByTestId('edit-activity-button').first();
    await editButton.click();

    // Verify form is pre-filled
    const editTypeSelect = page.getByTestId('edit-type-select');
    await expect(editTypeSelect).toHaveValue('bike');

    const editValueInput = page.getByTestId('edit-value-input');
    await expect(editValueInput).toHaveValue('15');

    const editDateInput = page.getByTestId('edit-date-input');
    await expect(editDateInput).toHaveValue(testDate);

    const editNotesInput = page.getByTestId('edit-notes-input');
    await expect(editNotesInput).toHaveValue('Bike to work');
  });

  test('delete dialog shows activity summary', async ({ page }) => {
    // Create activity
    const transportTab = page.getByTestId('category-tab-transport');
    if (!(await transportTab.isVisible({ timeout: 5000 }).catch(() => false))) {
      test.skip();
      return;
    }
    await transportTab.click();

    const typeSelect = page.getByTestId('transport-type-select');
    await typeSelect.selectOption('bus');

    const distanceInput = page.getByTestId('transport-distance-input');
    await distanceInput.fill('45');

    const dateInput = page.getByTestId('transport-date-input');
    const today = new Date().toISOString().split('T')[0];
    await dateInput.fill(today);

    const submitButton = page.getByTestId('log-transport-button');
    await submitButton.click();

    await expect(page.getByText(/45 km/)).toBeVisible({ timeout: 10000 });

    // Open delete dialog
    const deleteButton = page.getByTestId('delete-activity-button').first();
    await deleteButton.click();

    // Verify activity summary is shown
    await expect(page.getByText('Delete Activity?')).toBeVisible();
    await expect(page.getByText(/45 km/)).toBeVisible();
    await expect(page.getByText(/kg CO2e/)).toBeVisible();
  });
});
