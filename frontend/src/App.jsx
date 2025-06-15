import React, { useState, useEffect } from 'react';
import InputForm from './components/InputForm';
import RecommendationsDisplay from './components/RecommendationsDisplay';

// --- API Configuration ---
// For local development, your backend Python API (FastAPI/Flask)
// will likely be running on a different port (e.g., 8000).
// Vite's dev server (e.g., 5173) needs to be able to call it.
// You might need to configure CORS in your Python backend.
// (You already added CORSMiddleware to your FastAPI app, which is good!)

// When deploying to Azure Static Web Apps, you can configure a proxy
// so that requests to '/api' from your frontend are routed to your
// Azure Function backend. For local dev, we'll use the full URL.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'; // Default for local dev

function App() {
  const [recommendations, setRecommendations] = useState([]);
  const [recommendationTitle, setRecommendationTitle] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Placeholder for API calls
  const fetchRecommendations = async (titles) => {
    setIsLoading(true);
    setError(null);
    setRecommendations([]); // Clear previous recommendations
    try {
      const response = await fetch(`${API_BASE_URL}/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(titles), // Send as an array of strings
      });
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRecommendations(data.recommendations || []);
      setRecommendationTitle("Based on your choices:");
    } catch (err) {
      console.error("Failed to fetch recommendations:", err);
      setError(err.message);
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSurprise = async () => {
    setIsLoading(true);
    setError(null);
    setRecommendations([]);
    try {
      const response = await fetch(`${API_BASE_URL}/surprise`);
      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setRecommendations(data.surprises || []); // Assuming backend returns { "surprises": [...] }
      setRecommendationTitle("Surprise!");
    } catch (err) {
      console.error("Failed to fetch surprise:", err);
      setError(err.message);
      setRecommendations([]);
    } finally {
      setIsLoading(false);
    }
  };


  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      <header className="bg-gradient-to-r from-sky-500 to-indigo-600 text-white p-6 shadow-lg">
        <div className="container mx-auto">
          <h1 className="text-4xl font-bold text-center tracking-tight">Movie Recommender AI</h1>
          <p className="text-center text-sky-100 mt-1">Find your next binge-watch!</p>
        </div>
      </header>

      <main className="container mx-auto p-4 sm:p-8">
        <InputForm onRecommend={fetchRecommendations} onSurprise={fetchSurprise} />

        {error && (
          <div className="my-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded-md text-center" role="alert">
            <strong className="font-bold">Oops! </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}

        <RecommendationsDisplay 
          recommendations={recommendations} 
          title={recommendationTitle}
          isLoading={isLoading} 
        />
      </main>

      <footer className="text-center py-8 text-sm text-slate-500 border-t border-slate-200 mt-12">
        <p>&copy; {new Date().getFullYear()} Movie Recommender App. Built with React, FastAPI & Love.</p>
      </footer>
    </div>
  );
}

export default App;