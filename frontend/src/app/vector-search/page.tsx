'use client';

import { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import { saveRecommendation } from '@/services/spaceService';
import axios from 'axios';

interface SearchResult {
  id: string;
  score: number;
  oasis_code: string;
  label: string;
  lead_statement?: string;
  main_duties?: string;
  creativity?: number | null;
  leadership?: number | null;
  digital_literacy?: number | null;
  critical_thinking?: number | null;
  problem_solving?: number | null;
  analytical_thinking?: number | null;
  attention_to_detail?: number | null;
  collaboration?: number | null;
  adaptability?: number | null;
  independence?: number | null;
  evaluation?: number | null;
  decision_making?: number | null;
  stress_tolerance?: number | null;
  all_fields?: { [key: string]: string };
}

interface SkillValues {
  role_creativity?: number | null;
  role_leadership?: number | null;
  role_digital_literacy?: number | null;
  role_critical_thinking?: number | null;
  role_problem_solving?: number | null;
  analytical_thinking?: number | null;
  attention_to_detail?: number | null;
  collaboration?: number | null;
  adaptability?: number | null;
  independence?: number | null;
  evaluation?: number | null;
  decision_making?: number | null;
  problem_solving?: number | null;
  stress_tolerance?: number | null;
}

export default function VectorSearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [savingIds, setSavingIds] = useState<Set<string>>(new Set());
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSaveSuccess(null);

    try {
      console.log('API URL:', process.env.NEXT_PUBLIC_API_URL);
      console.log('Making search request with query:', query);
      
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL}/vector/search`, {
        query: query
      });
      
      console.log('Search response:', response.data);
      const data = response.data as { results: SearchResult[] };
      setResults(data.results);
    } catch (err) {
      console.error('Search error:', err);
      setError('Failed to search. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  async function handleSaveToSpace(result: SearchResult) {
    try {
      setSavingIds(prev => new Set(prev).add(result.id));
      setSaveSuccess(null);

      const recommendation = {
        oasis_code: result.oasis_code,
        label: result.label,
        description: result.lead_statement || '',
        main_duties: result.main_duties || '',
        role_creativity: result.creativity ?? 0,
        role_leadership: result.leadership ?? 0,
        role_digital_literacy: result.digital_literacy ?? 0,
        role_critical_thinking: result.critical_thinking ?? 0,
        role_problem_solving: result.problem_solving ?? 0,
        analytical_thinking: result.analytical_thinking ?? 0,
        attention_to_detail: result.attention_to_detail ?? 0,
        collaboration: result.collaboration ?? 0,
        adaptability: result.adaptability ?? 0,
        independence: result.independence ?? 0,
        evaluation: result.evaluation ?? 0,
        decision_making: result.decision_making ?? 0,
        stress_tolerance: result.stress_tolerance ?? 0,
        all_fields: result.all_fields || {}
      };

      await saveRecommendation(recommendation);

      setSaveSuccess(`Successfully saved "${result.label}" to your Space`);
      setSavingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(result.id);
        return newSet;
      });

      setTimeout(() => {
        setSaveSuccess(null);
      }, 3000);
    } catch (err: any) {
      if (err.response?.status === 400 && err.response?.data?.detail === "This recommendation is already saved.") {
        setError('This recommendation is already in your Space.');
      } else {
        setError('Failed to save to Space. Please try again.');
      }
      console.error('Save error:', err);
      setSavingIds(prev => {
        const newSet = new Set(prev);
        newSet.delete(result.id);
        return newSet;
      });
    }
  }

  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6 gradient-text">Career Recommendations</h1>

        <form onSubmit={handleSearch} className="mb-8">
          <div className="search-header">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter skills, interests, or desired career..."
              className="search-header__input"
            />
            <button
              type="submit"
              disabled={loading}
              className="search-header__button"
            >
              <svg className="search-header__icon" viewBox="0 0 24 24">
                <path d="M15.5 14h-.79l-.28-.27C15.41 12.59 16 11.11 16 9.5 16 5.91 13.09 3 9.5 3S3 5.91 3 9.5 5.91 16 9.5 16c1.61 0 3.09-.59 4.23-1.57l.27.28v.79l5 4.99L20.49 19l-4.99-5zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z"/>
              </svg>
            </button>
          </div>
          {error && <p className="text-red-400 mt-2">{error}</p>}
          {saveSuccess && (
            <div className="mt-2 p-2 bg-green-500/20 text-green-300 rounded-lg text-sm">
              {saveSuccess}
            </div>
          )}
        </form>

        <div>
          {results.length > 0 ? (
            <div>
              <h2 className="text-xl font-semibold mb-4">Search Results</h2>
              <div className="space-y-6">
                {results.map((result) => (
                  <div key={result.id} className="card p-6 bg-white/5 backdrop-blur-sm border border-white/10 rounded-lg">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="text-xl font-bold text-primary-teal">{result.label || 'No label available'}</h3>
                      <div className="flex items-center gap-2">
                        <span className="text-sm bg-primary-purple/30 text-primary-teal px-2 py-1 rounded-full">
                          Match: {(result.score * 100).toFixed(0)}%
                        </span>
                        <button
                          onClick={() => handleSaveToSpace(result)}
                          disabled={savingIds.has(result.id)}
                          className="btn btn-sm btn-secondary"
                        >
                          {savingIds.has(result.id) ? 'Saving...' : 'Save to Space'}
                        </button>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <p className="text-sm text-neutral-600">Job title: {result.label}</p>
                      {result.lead_statement && (
                        <div>
                          <h4 className="font-medium text-sm text-neutral-600 mb-1">Description</h4>
                          <p className="text-sm text-neutral-600">{result.lead_statement}</p>
                        </div>
                      )}
                      {result.main_duties && (
                        <div>
                          <h4 className="font-medium text-sm text-neutral-600 mb-1">Main Duties</h4>
                          <p className="text-sm text-neutral-600">{result.main_duties}</p>
                        </div>
                      )}
                      {(result.creativity || result.leadership || result.digital_literacy || result.critical_thinking || result.problem_solving) && (
                        <div className="mt-4">
                          <h4 className="font-medium text-sm text-neutral-600 mb-1">Key Skills</h4>
                          <ul className="text-sm text-neutral-600 grid grid-cols-2 gap-x-4 gap-y-1">
                            {result.creativity !== null && (
                              <li><span className="font-semibold">Creativity:</span> {result.creativity}</li>
                            )}
                            {result.leadership !== null && (
                              <li><span className="font-semibold">Leadership:</span> {result.leadership}</li>
                            )}
                            {result.digital_literacy !== null && (
                              <li><span className="font-semibold">Digital Literacy:</span> {result.digital_literacy}</li>
                            )}
                            {result.critical_thinking !== null && (
                              <li><span className="font-semibold">Critical Thinking:</span> {result.critical_thinking}</li>
                            )}
                            {result.problem_solving !== null && (
                              <li><span className="font-semibold">Problem Solving:</span> {result.problem_solving}</li>
                            )}
                          </ul>
                        </div>
                      )}
                        
                      <p className="text-xs text-neutral-500 italic mt-2">
                        Save to your Space to view all job details and requirements
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            !loading && (
              <div className="text-center text-neutral-600 py-12">
                <p>No results to display. Try searching for occupations or skills.</p>
                <p className="mt-2 text-sm">Example searches: "software developer", "healthcare", "creative jobs"</p>
              </div>
            )
          )}
        </div>
      </div>
    </MainLayout>
  );
}