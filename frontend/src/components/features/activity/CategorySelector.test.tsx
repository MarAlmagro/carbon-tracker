import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { I18nextProvider } from 'react-i18next';
import { describe, it, expect, vi } from 'vitest';
import i18n from '@/i18n';
import CategorySelector from './CategorySelector';

const renderWithI18n = (ui: React.ReactElement) =>
  render(<I18nextProvider i18n={i18n}>{ui}</I18nextProvider>);

describe('CategorySelector', () => {
  it('renders all three category tabs', () => {
    renderWithI18n(<CategorySelector value="transport" onChange={vi.fn()} />);

    expect(screen.getByTestId('category-tab-transport')).toBeInTheDocument();
    expect(screen.getByTestId('category-tab-energy')).toBeInTheDocument();
    expect(screen.getByTestId('category-tab-food')).toBeInTheDocument();
  });

  it('renders category labels from i18n', () => {
    renderWithI18n(<CategorySelector value="transport" onChange={vi.fn()} />);

    expect(screen.getByText('Transport')).toBeInTheDocument();
    expect(screen.getByText('Home Energy')).toBeInTheDocument();
    expect(screen.getByText('Food & Diet')).toBeInTheDocument();
  });

  it('marks the active category with aria-pressed', () => {
    renderWithI18n(<CategorySelector value="energy" onChange={vi.fn()} />);

    expect(screen.getByTestId('category-tab-energy')).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByTestId('category-tab-transport')).toHaveAttribute('aria-pressed', 'false');
    expect(screen.getByTestId('category-tab-food')).toHaveAttribute('aria-pressed', 'false');
  });

  it('calls onChange when a category tab is clicked', async () => {
    const onChange = vi.fn();
    const user = userEvent.setup();
    renderWithI18n(<CategorySelector value="transport" onChange={onChange} />);

    await user.click(screen.getByTestId('category-tab-energy'));
    expect(onChange).toHaveBeenCalledWith('energy');

    await user.click(screen.getByTestId('category-tab-food'));
    expect(onChange).toHaveBeenCalledWith('food');
  });

  it('applies active styling to the selected category', () => {
    renderWithI18n(<CategorySelector value="food" onChange={vi.fn()} />);

    const foodTab = screen.getByTestId('category-tab-food');
    expect(foodTab.className).toContain('border-blue-600');
    expect(foodTab.className).toContain('text-blue-600');
  });

  it('has accessible aria-labels on each tab', () => {
    renderWithI18n(<CategorySelector value="transport" onChange={vi.fn()} />);

    expect(screen.getByTestId('category-tab-transport')).toHaveAttribute('aria-label', 'Transport');
    expect(screen.getByTestId('category-tab-energy')).toHaveAttribute('aria-label', 'Home Energy');
    expect(screen.getByTestId('category-tab-food')).toHaveAttribute('aria-label', 'Food & Diet');
  });

  it('renders the category-selector container', () => {
    renderWithI18n(<CategorySelector value="transport" onChange={vi.fn()} />);

    expect(screen.getByTestId('category-selector')).toBeInTheDocument();
  });
});
