'use client';

import React from 'react';
import { Job } from './JobCard';
import styles from './JobRecommendationVerticalList.module.css';

interface JobRecommendationVerticalListProps {
  jobs: Job[];
  onJobClick?: (job: Job) => void;
  onSaveJob?: (job: Job) => void;
  className?: string;
}

const JobRecommendationVerticalList: React.FC<JobRecommendationVerticalListProps> = ({
  jobs,
  onJobClick,
  onSaveJob,
  className = ''
}) => {
  return (
    <div className={`${styles.container} ${className}`}>
      <h2 className={styles.title}>Recommended Jobs</h2>
      <div className={styles.jobsList}>
        {jobs.map((job) => (
          <div
            key={job.id}
            className={styles.jobCard}
            onClick={() => onJobClick?.(job)}
          >
            <div className={styles.jobHeader}>
              <h3 className={styles.jobTitle}>{job.metadata.preferred_label || job.metadata.title}</h3>
              <button
                className={styles.saveButton}
                onClick={(e) => {
                  e.stopPropagation();
                  onSaveJob?.(job);
                }}
                title="Save job"
              >
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
                  <path d="M184,32H72A16,16,0,0,0,56,48V224a8,8,0,0,0,12.24,6.78L128,193.43l59.77,37.35A8,8,0,0,0,200,224V48A16,16,0,0,0,184,32Z"></path>
                </svg>
              </button>
            </div>
            
            <p className={styles.jobDescription}>{job.metadata.description}</p>
            
            <div className={styles.jobSkills}>
              {job.metadata.skills && job.metadata.skills.slice(0, 4).map((skill, index) => (
                <span key={index} className={styles.skillTag}>
                  {skill}
                </span>
              ))}
            </div>
            
            <div className={styles.jobFooter}>
              <button className={styles.exploreButton}>
                Explore
                <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JobRecommendationVerticalList;