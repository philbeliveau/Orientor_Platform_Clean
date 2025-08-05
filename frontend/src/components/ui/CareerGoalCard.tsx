'use client';

import React from 'react';
import Link from 'next/link';

interface CareerGoalCardProps {
  style?: React.CSSProperties;
  className?: string;
}

export default function CareerGoalCard({ style, className = '' }: CareerGoalCardProps) {
  // Mock career goal data
  const careerGoal = {
    title: "Become a Senior Data Scientist",
    description: "Lead machine learning projects and mentor junior developers in AI/ML technologies",
    targetDate: "December 2025",
    progress: 65,
    milestones: [
      { task: "Complete Advanced ML Certification", completed: true },
      { task: "Lead 2 ML Projects", completed: true },
      { task: "Publish Research Paper", completed: false },
      { task: "Build Team Leadership Skills", completed: false }
    ]
  };

  const completedMilestones = careerGoal.milestones.filter(m => m.completed).length;
  const totalMilestones = careerGoal.milestones.length;

  return (
    <div 
      className={`relative ${className}`}
      style={style}
    >
      <div className="h-full p-6 flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex-1">
            <h2 className="text-lg font-semibold mb-1" style={{ color: '#000000' }}>
              Career Goal
            </h2>
            <div className="flex items-center gap-2">
              <svg width="16" height="16" fill="#22c55e" viewBox="0 0 24 24">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
              </svg>
              <span className="text-xs text-gray-600">Target: {careerGoal.targetDate}</span>
            </div>
          </div>
          
          <Link
            href="/goals"
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            <span>Manage</span>
            <svg width="16" height="16" fill="currentColor" viewBox="0 0 256 256">
              <path d="M221.66,133.66l-72,72a8,8,0,0,1-11.32-11.32L196.69,136H40a8,8,0,0,1,0-16H196.69L138.34,61.66a8,8,0,0,1,11.32-11.32l72,72A8,8,0,0,1,221.66,133.66Z"></path>
            </svg>
          </Link>
        </div>

        {/* Goal Title */}
        <h3 className="text-base font-bold mb-2 text-gray-800 line-clamp-2">
          {careerGoal.title}
        </h3>
        
        {/* Goal Description */}
        <p className="text-sm text-gray-600 mb-4 line-clamp-2 flex-1">
          {careerGoal.description}
        </p>

        {/* Progress Section */}
        <div className="space-y-3">
          {/* Progress Bar */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-700">Overall Progress</span>
              <span className="text-xs font-bold text-blue-600">{careerGoal.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${careerGoal.progress}%` }}
              ></div>
            </div>
          </div>

          {/* Milestones */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-gray-700">Milestones</span>
              <span className="text-xs text-gray-600">{completedMilestones}/{totalMilestones}</span>
            </div>
            <div className="space-y-1">
              {careerGoal.milestones.slice(0, 2).map((milestone, index) => (
                <div key={index} className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full border-2 flex items-center justify-center ${
                    milestone.completed 
                      ? 'bg-green-500 border-green-500' 
                      : 'border-gray-300 bg-white'
                  }`}>
                    {milestone.completed && (
                      <svg width="8" height="8" fill="white" viewBox="0 0 24 24">
                        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/>
                      </svg>
                    )}
                  </div>
                  <span className={`text-xs ${
                    milestone.completed ? 'text-gray-700 line-through' : 'text-gray-600'
                  }`}>
                    {milestone.task}
                  </span>
                </div>
              ))}
              {careerGoal.milestones.length > 2 && (
                <div className="text-xs text-gray-500 pl-5">
                  +{careerGoal.milestones.length - 2} more milestones
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}