import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import InputForm from '../InputForm';
import { describe, it, expect, vi, afterEach } from 'vitest'; // Added afterEach
import { fireEvent } from '@testing-library/react';

// Store the original window.alert if you want to restore it perfectly
const originalAlert = window.alert;

afterEach(() => {
  // Restore window.alert after each test in this file to avoid interference
  // or clear mocks if just using vi.fn()
  vi.restoreAllMocks(); // This restores spies and clears mocks created with vi.fn() if used with vi.spyOn
  window.alert = originalAlert; // More explicit restoration for direct assignment
});

describe('InputForm Component', () => {
  it('renders all three input fields and buttons', () => {
    render(<InputForm onRecommend={() => {}} onSurprise={() => {}} />);

    expect(screen.getByLabelText(/Movie\/Series 1:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Movie\/Series 2:/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Movie\/Series 3:/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Get Recommendations/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Surprise Me!/i })).toBeInTheDocument();
  });

  it('updates input values on change', async () => {
    const user = userEvent.setup();
    render(<InputForm onRecommend={() => {}} onSurprise={() => {}} />);

    const movie1Input = screen.getByLabelText(/Movie\/Series 1:/i);
    await user.type(movie1Input, 'Inception');
    expect(movie1Input).toHaveValue('Inception');

    const movie2Input = screen.getByLabelText(/Movie\/Series 2:/i);
    await user.type(movie2Input, 'The Matrix');
    expect(movie2Input).toHaveValue('The Matrix');
  });

  it('calls onRecommend with input values when form is submitted with all fields filled', async () => {
    const user = userEvent.setup();
    const mockOnRecommend = vi.fn(); // Vitest's way of creating a spy/mock function

    render(<InputForm onRecommend={mockOnRecommend} onSurprise={() => {}} />);

    await user.type(screen.getByLabelText(/Movie\/Series 1:/i), 'Movie A');
    await user.type(screen.getByLabelText(/Movie\/Series 2:/i), 'Movie B');
    await user.type(screen.getByLabelText(/Movie\/Series 3:/i), 'Movie C');

    await user.click(screen.getByRole('button', { name: /Get Recommendations/i }));

    expect(mockOnRecommend).toHaveBeenCalledTimes(1);
    expect(mockOnRecommend).toHaveBeenCalledWith(['Movie A', 'Movie B', 'Movie C']);
  });

  it('shows alert and does not call onRecommend if not all fields are filled - by directly calling submit', async () => {
    const user = userEvent.setup();
    const mockOnRecommend = vi.fn();
    const mockAlertFn = vi.fn();
    window.alert = mockAlertFn;

    const { container } = render(<InputForm onRecommend={mockOnRecommend} onSurprise={() => {}} />);

    // Fill one input
    await user.type(screen.getByLabelText(/Movie\/Series 1:/i), 'Movie A');
    // Leave others empty

    // Instead of clicking the button, find the form and directly fire its submit event
    // This bypasses some of the button-click-induced native validation behaviors
    // that might differ subtly in JSDOM vs. a real browser.
    const form = container.querySelector('form');
    fireEvent.submit(form); // Using fireEvent here for direct event dispatch

    expect(mockOnRecommend).not.toHaveBeenCalled();
    console.log('Actual alert calls (direct submit):', mockAlertFn.mock.calls);
    expect(mockAlertFn).toHaveBeenCalledTimes(1); 
    expect(mockAlertFn).toHaveBeenCalledWith('Please enter three movie titles.');
    });

  it('does not call onRecommend when required fields are empty and submit button is clicked', async () => {
  const user = userEvent.setup();
  const mockOnRecommend = vi.fn();
  // We don't mock window.alert here because we expect native validation to prevent submit,
  // so our custom alert shouldn't even be reached.

  render(<InputForm onRecommend={mockOnRecommend} onSurprise={() => {}} />);

  await user.type(screen.getByLabelText(/Movie\/Series 1:/i), 'Movie A');
  // Movie 2 and 3 are left empty, and they have 'required' attributes.

  await user.click(screen.getByRole('button', { name: /Get Recommendations/i }));

  // Due to 'required', the onSubmit handler (and thus onRecommend) should not be called.
  expect(mockOnRecommend).not.toHaveBeenCalled(); 
  });

  it('calls onSurprise when "Surprise Me!" button is clicked', async () => {
    const user = userEvent.setup();
    const mockOnSurprise = vi.fn();

    render(<InputForm onRecommend={() => {}} onSurprise={mockOnSurprise} />);

    await user.click(screen.getByRole('button', { name: /Surprise Me!/i }));

    expect(mockOnSurprise).toHaveBeenCalledTimes(1);
  });
});