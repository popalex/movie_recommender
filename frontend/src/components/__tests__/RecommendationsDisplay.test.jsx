import { render, screen } from '@testing-library/react';
import RecommendationsDisplay from '../RecommendationsDisplay'; // Adjust path
import { describe, it, expect } from 'vitest';

const mockRecommendations = [
  { id: 1, title: 'Test Movie 1', overview: 'Overview 1', release_year: 2020, poster_url: 'poster1.jpg' },
  { id: 2, title: 'Test Movie 2', overview: 'Overview 2', release_year: 2021, poster_url: null }, // Test no poster
];

describe('RecommendationsDisplay Component', () => {
  it('renders loading state correctly', () => {
    render(<RecommendationsDisplay recommendations={[]} title="Loading..." isLoading={true} />);
    expect(screen.getByText(/Fetching recommendations.../i)).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument(); // Use getByTestId
    expect(screen.getByTestId('loading-spinner')).toHaveClass('animate-spin'); // You can also check for specific classes
  });

  it('renders "no recommendations" message when recommendations array is empty and not loading', () => {
    render(<RecommendationsDisplay recommendations={[]} title="Recommendations" isLoading={false} />);
    expect(screen.getByText(/Enter movies above or click "Surprise Me!" to get recommendations./i)).toBeInTheDocument();
  });

  it('renders "no recommendations" message when recommendations prop is null and not loading', () => {
    render(<RecommendationsDisplay recommendations={null} title="Recommendations" isLoading={false} />);
    expect(screen.getByText(/Enter movies above or click "Surprise Me!" to get recommendations./i)).toBeInTheDocument();
  });

  it('renders recommendation cards correctly', () => {
    render(<RecommendationsDisplay recommendations={mockRecommendations} title="Your Recs" isLoading={false} />);

    expect(screen.getByText('Your Recs')).toBeInTheDocument();
    expect(screen.getByText('Test Movie 1')).toBeInTheDocument();
    expect(screen.getByText('Overview 1')).toBeInTheDocument();
    expect(screen.getByText('(2020)')).toBeInTheDocument();
    expect(screen.getByAltText('Test Movie 1')).toHaveAttribute('src', 'poster1.jpg');

    expect(screen.getByText('Test Movie 2')).toBeInTheDocument();
    expect(screen.getByText('Overview 2')).toBeInTheDocument();
    // Check for "No Poster" text when poster_url is null
    const movieCard2 = screen.getByText('Test Movie 2').closest('div.bg-white'); // Find parent card
    expect(movieCard2).toHaveTextContent('No Poster');
  });

  it('uses a default title if no title prop is provided', () => {
    render(<RecommendationsDisplay recommendations={mockRecommendations} isLoading={false} />);
    expect(screen.getByText('Here are your recommendations:')).toBeInTheDocument();
  });
});