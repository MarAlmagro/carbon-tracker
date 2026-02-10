import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { AppShell } from './AppShell';

describe('AppShell', () => {
  it('renders the navigation', () => {
    render(
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    );

    expect(screen.getByText('Carbon Tracker')).toBeInTheDocument();
  });

  it('renders the footer', () => {
    render(
      <BrowserRouter>
        <AppShell />
      </BrowserRouter>
    );

    expect(screen.getByText(/© 2026 Carbon Footprint Tracker/)).toBeInTheDocument();
  });
});
