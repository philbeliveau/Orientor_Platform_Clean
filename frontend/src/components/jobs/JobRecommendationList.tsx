'use client';

import React, { useState } from 'react';
import JobCard, { Job } from './JobCard';
import LoadingSpinner from '@/components/ui/LoadingSpinner';
import { useRouter } from 'next/navigation';

interface JobRecommendationListProps {
  recommendations: Job[];
  isLoading: boolean;
  error: string | null;
  onSelectJob: (job: Job) => void;
  className?: string;
}

const JobRecommendationList: React.FC<JobRecommendationListProps> = ({
  recommendations,
  isLoading,
  error,
  onSelectJob,
  className = '',
}) => {
  const router = useRouter();
  const [selectedJobId, setSelectedJobId] = useState<string | null>(
    recommendations.length > 0 ? recommendations[0].id : null
  );

  // Gérer la sélection d'un emploi
  const handleSelectJob = (job: Job) => {
    setSelectedJobId(job.id);
    onSelectJob(job);
  };

  const handleViewMore = () => {
    router.push('/career/recommendations');
  };

  // Afficher un état de chargement
  if (isLoading) {
    return (
      <div className={`flex justify-center items-center p-8 ${className}`}>
        <LoadingSpinner size="lg" />
        <p className="ml-3" style={{ color: 'var(--text-color)' }}>Chargement des recommandations...</p>
      </div>
    );
  }

  // Afficher un message d'erreur
  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <p className="text-red-600">
          Erreur lors du chargement des recommandations: {error}
        </p>
      </div>
    );
  }

  // Afficher un message si aucune recommandation n'est disponible
  if (recommendations.length === 0) {
    return (
      <div className={`bg-stitch-primary border border-stitch-border rounded-lg p-6 text-center ${className}`}>
        <p style={{ color: 'var(--text-color)' }}>
          Aucune recommandation d'emploi disponible pour le moment.
        </p>
        <p className="text-sm mt-2" style={{ color: 'var(--text-color)' }}>
          Complétez votre profil pour obtenir des recommandations personnalisées.
        </p>
      </div>
    );
  }

  return (
    <div className={`w-full ${className}`}>
      <h2 className="text-[22px] md:text-2xl font-bold leading-tight tracking-[-0.015em] mb-4 font-departure" style={{ color: 'var(--accent-color)' }}>
        {/* Explorez vos meilleures correspondances d'emploi */}
      </h2>
      
      <style jsx global>{`
        .container {
          position: relative;
          display: flex;
          justify-content: center;
          align-items: center;
          min-width: 180px;
          height: 200px;
        }

        .container .glass {
          position: relative;
          width: 180px;
          height: 200px;
          background: linear-gradient(#fff2, transparent);
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 25px 25px rgba(0, 0, 0, 0.25);
          display: flex;
          justify-content: center;
          align-items: center;
          transition: 0.5s;
          border-radius: 10px;
          margin: 0 -45px;
          backdrop-filter: blur(10px);
          transform: rotate(calc(var(--r) * 1deg));
        }

        .container:hover .glass {
          transform: rotate(0deg);
          margin: 0 10px;
        }

        .container .glass::before {
          content: attr(data-text);
          position: absolute;
          bottom: 0;
          width: 100%;
          height: 40px;
          background: rgba(255, 255, 255, 0.05);
          display: flex;
          justify-content: center;
          align-items: center;
          color: var(--text-color);
          font-size: 0.9rem;
          padding: 0 10px;
          text-align: center;
        }

        .cards-container {
          display: flex;
          justify-content: center;
          align-items: center;
          gap: 0;
          padding: 2rem 0;
          perspective: 1000px;
        }

        .cards-container > *:nth-child(1) {
          --r: -15;
        }

        .cards-container > *:nth-child(2) {
          --r: 0;
          z-index: 1;
        }

        .cards-container > *:nth-child(3) {
          --r: 15;
        }

        .cards-container:hover > *:nth-child(1) {
          --r: -15;
          margin: 0 -45px;
        }

        .cards-container:hover > *:nth-child(2) {
          --r: 0;
          margin: 0 10px;
        }

        .cards-container:hover > *:nth-child(3) {
          --r: 15;
          margin: 0 -45px;
        }
      `}</style>
      
      <div className="cards-container">
        {recommendations.map((job) => (
          <JobCard
            key={job.id}
            job={job}
            isSelected={job.id === selectedJobId}
            onClick={() => handleSelectJob(job)}
          />
        ))}
      </div>
      
      {recommendations.length > 0 && (
        <div className="mt-4 text-right">
          <button
            className="text-sm hover:underline focus:outline-none"
            style={{ color: 'var(--accent-color)' }}
            onClick={handleViewMore}
          >
            Voir plus de recommandations →
          </button>
        </div>
      )}
    </div>
  );
};

export default JobRecommendationList;