import React, { useState } from 'react';

const InputForm = ({ onRecommend, onSurprise }) => {
  const [movie1, setMovie1] = useState('');
  const [movie2, setMovie2] = useState('');
  const [movie3, setMovie3] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (movie1 && movie2 && movie3) {
      onRecommend([movie1, movie2, movie3]);
    } else {
      // Basic validation, you can make this more user-friendly
      alert('Please enter three movie titles.');
    }
  };

  const inputClasses = "mt-1 block w-full px-3 py-2 bg-white border border-slate-300 rounded-md text-sm shadow-sm placeholder-slate-400 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 disabled:bg-slate-50 disabled:text-slate-500 disabled:border-slate-200 disabled:shadow-none invalid:border-pink-500 invalid:text-pink-600 focus:invalid:border-pink-500 focus:invalid:ring-pink-500";

  return (
    <div className="mb-8 p-6 bg-slate-100 rounded-lg shadow-md">
      <form onSubmit={handleSubmit}>
        <h2 className="text-2xl font-semibold text-slate-700 mb-4">Tell us 3 movies/series you like:</h2>
        <div className="space-y-4 mb-6">
          <div>
            <label htmlFor="movie1" className="block text-sm font-medium text-slate-700">Movie/Series 1:</label>
            <input
              type="text"
              id="movie1"
              value={movie1}
              onChange={(e) => setMovie1(e.target.value)}
              className={inputClasses}
              placeholder="e.g., Inception"
              required
            />
          </div>
          <div>
            <label htmlFor="movie2" className="block text-sm font-medium text-slate-700">Movie/Series 2:</label>
            <input
              type="text"
              id="movie2"
              value={movie2}
              onChange={(e) => setMovie2(e.target.value)}
              className={inputClasses}
              placeholder="e.g., Breaking Bad"
              required
            />
          </div>
          <div>
            <label htmlFor="movie3" className="block text-sm font-medium text-slate-700">Movie/Series 3:</label>
            <input
              type="text"
              id="movie3"
              value={movie3}
              onChange={(e) => setMovie3(e.target.value)}
              className={inputClasses}
              placeholder="e.g., Stranger Things"
              required
            />
          </div>
        </div>
        <div className="flex flex-col sm:flex-row sm:space-x-4 space-y-2 sm:space-y-0">
          <button
            type="submit"
            className="w-full sm:w-auto px-6 py-3 bg-sky-600 text-white font-semibold rounded-lg shadow-md hover:bg-sky-700 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-opacity-75 transition duration-150 ease-in-out"
          >
            Get Recommendations
          </button>
          <button
            type="button"
            onClick={onSurprise}
            className="w-full sm:w-auto px-6 py-3 bg-emerald-500 text-white font-semibold rounded-lg shadow-md hover:bg-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-400 focus:ring-opacity-75 transition duration-150 ease-in-out"
          >
            Surprise Me!
          </button>
        </div>
      </form>
    </div>
  );
};

export default InputForm;