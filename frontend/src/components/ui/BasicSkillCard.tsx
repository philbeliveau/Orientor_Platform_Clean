'use client';

import React from 'react';
import styles from './BasicSkillCard.module.css';

interface BasicSkillCardProps {
  skill: {
    name: string;
    description: string;
    icon: string;
  };
  className?: string;
  onClick?: (skillName: string) => void;
}

const BasicSkillCard: React.FC<BasicSkillCardProps> = ({ skill, className = '', onClick }) => {
  return (
    <div className={`${styles.cardContainer} ${className}`}>
      <div 
        className={styles.card}
        onClick={() => onClick?.(skill.name)}
      >
        {/* Skill icon */}
        <div className={styles.icon}>
          {skill.icon}
        </div>
        
        {/* Skill title */}
        <div className={styles.city}>
          {skill.name}
        </div>
        
        {/* Skill description */}
        <div className={styles.weather}>
          {skill.description}
        </div>
      </div>
    </div>
  );
};

export default BasicSkillCard;