import React from 'react';

const MovieCard = ({ movie }) => (
  <div className="bg-white rounded-lg shadow-lg overflow-hidden transform hover:scale-105 transition-transform duration-300">
    {movie.poster_url ? (
      <img src={movie.poster_url} alt={movie.title} className="w-full h-72 object-cover" />
    ) : (
      <div className="w-full h-72 bg-gray-200 flex items-center justify-center">
        <span className="text-gray-500">No Poster</span>
      </div>
    )}
    <div className="p-4">
      <h3 className="text-lg font-semibold text-slate-800 mb-1">{movie.title}</h3>
      {movie.release_year && <p className="text-sm text-slate-600 mb-2">({movie.release_year})</p>}
      <p className="text-xs text-slate-500 line-clamp-3">{movie.overview}</p>
    </div>
  </div>
);


const RecommendationsDisplay = ({ recommendations, title, isLoading }) => {
  if (isLoading) {
    return (
      <div className="text-center py-10">
      <div 
        data-testid="loading-spinner" // Add this
        className="animate-spin rounded-full h-12 w-12 border-b-2 border-sky-500 mx-auto"
      ></div>
      <p className="mt-2 text-slate-600">Fetching recommendations...</p>
    </div>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return <div className="text-center py-10 text-slate-500">Enter movies above or click "Surprise Me!" to get recommendations.</div>;
  }

  return (
    <div className="mt-8">
      <h2 className="text-3xl font-bold text-slate-800 mb-6 text-center">{title || "Here are your recommendations:"}</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {recommendations.map((movie) => (
          <MovieCard key={movie.id || movie.title} movie={movie} />
        ))}
      </div>
    </div>
  );
};

export default RecommendationsDisplay;