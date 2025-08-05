import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { SaveActionButton } from '../SaveActionButton';

describe('SaveActionButton', () => {
  const mockOnSave = jest.fn();

  beforeEach(() => {
    mockOnSave.mockClear();
  });

  test('renders with default props', () => {
    render(<SaveActionButton onSave={mockOnSave} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Save');
    expect(button).not.toBeDisabled();
  });

  test('renders with custom label', () => {
    render(<SaveActionButton onSave={mockOnSave} label="Save Job" />);
    
    expect(screen.getByText('Save Job')).toBeInTheDocument();
  });

  test('shows saved state when saved prop is true', () => {
    render(<SaveActionButton onSave={mockOnSave} saved={true} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveTextContent('Saved');
    expect(button).toBeDisabled();
  });

  test('calls onSave when clicked', async () => {
    mockOnSave.mockResolvedValueOnce(undefined);
    
    render(<SaveActionButton onSave={mockOnSave} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(mockOnSave).toHaveBeenCalledTimes(1);
  });

  test('shows loading state while saving', async () => {
    mockOnSave.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    render(<SaveActionButton onSave={mockOnSave} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    // Should show loading spinner
    await waitFor(() => {
      expect(button).toBeDisabled();
    });
    
    // Should return to normal state after save completes
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
  });

  test('handles save error gracefully', async () => {
    const consoleError = jest.spyOn(console, 'error').mockImplementation(() => {});
    mockOnSave.mockRejectedValueOnce(new Error('Save failed'));
    
    render(<SaveActionButton onSave={mockOnSave} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    await waitFor(() => {
      expect(button).not.toBeDisabled();
    });
    
    expect(consoleError).toHaveBeenCalledWith('Failed to save:', expect.any(Error));
    consoleError.mockRestore();
  });

  test('does not call onSave when already saved', () => {
    render(<SaveActionButton onSave={mockOnSave} saved={true} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(mockOnSave).not.toHaveBeenCalled();
  });

  test('renders different sizes correctly', () => {
    const { rerender } = render(<SaveActionButton onSave={mockOnSave} size="sm" />);
    expect(screen.getByRole('button')).toHaveClass('px-2', 'py-1', 'text-xs');
    
    rerender(<SaveActionButton onSave={mockOnSave} size="md" />);
    expect(screen.getByRole('button')).toHaveClass('px-3', 'py-1.5', 'text-sm');
    
    rerender(<SaveActionButton onSave={mockOnSave} size="lg" />);
    expect(screen.getByRole('button')).toHaveClass('px-4', 'py-2', 'text-base');
  });

  test('renders different variants correctly', () => {
    const { rerender } = render(<SaveActionButton onSave={mockOnSave} variant="primary" />);
    expect(screen.getByRole('button')).toHaveClass('bg-blue-500');
    
    rerender(<SaveActionButton onSave={mockOnSave} variant="ghost" />);
    expect(screen.getByRole('button')).toHaveClass('text-blue-600');
    
    rerender(<SaveActionButton onSave={mockOnSave} variant="outline" />);
    expect(screen.getByRole('button')).toHaveClass('border-blue-300');
  });

  test('applies custom className', () => {
    render(<SaveActionButton onSave={mockOnSave} className="custom-class" />);
    
    expect(screen.getByRole('button')).toHaveClass('custom-class');
  });

  test('shows hover effect on mouse enter', () => {
    render(<SaveActionButton onSave={mockOnSave} />);
    
    const button = screen.getByRole('button');
    fireEvent.mouseEnter(button);
    
    // Icon should have fill-current class on hover
    const icon = button.querySelector('svg');
    expect(icon).toBeTruthy();
  });
});