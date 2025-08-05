'use client';
import React, { useState } from 'react';
import { 
  Radar, 
  RadarChart, 
  PolarGrid, 
  PolarAngleAxis, 
  PolarRadiusAxis, 
  ResponsiveContainer,
  Tooltip
} from 'recharts';

// Sample data - in production this would come from the user's profile and the selected career
const sampleData = [
  { skill: 'Communication', userValue: 3, careerValue: 5, fullMark: 7 },
  { skill: 'Analytical Thinking', userValue: 5, careerValue: 6, fullMark: 7 },
  { skill: 'Technical Skills', userValue: 4, careerValue: 7, fullMark: 7 },
  { skill: 'Creativity', userValue: 6, careerValue: 4, fullMark: 7 },
  { skill: 'Attention to Detail', userValue: 4, careerValue: 6, fullMark: 7 },
  { skill: 'Problem Solving', userValue: 5, careerValue: 7, fullMark: 7 },
  { skill: 'Management', userValue: 3, careerValue: 5, fullMark: 7 },
  { skill: 'Adaptability', userValue: 5, careerValue: 4, fullMark: 7 },
];

// Custom tooltip component
const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const skill = payload[0].payload.skill;
    const userValue = payload[0].payload.userValue;
    const careerValue = payload[0].payload.careerValue;
    
    return (
      <div className="bg-white p-3 shadow-md rounded-md border border-gray-200">
        <p className="font-medium text-gray-800">{skill}</p>
        <p className="text-primary-purple">Your skill: {userValue}/7</p>
        <p className="text-primary-teal">Target requirement: {careerValue}/7</p>
      </div>
    );
  }

  return null;
};

export default function SkillSpiderChart() {
  // In a real app, you might have state to switch between different careers
  const [selectedCareer, setSelectedCareer] = useState('Product Manager');
  
  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={sampleData}>
          <PolarGrid stroke="#e0e0e0" />
          <PolarAngleAxis dataKey="skill" tick={{ fill: '#666', fontSize: 12 }} />
          <PolarRadiusAxis angle={90} domain={[0, 7]} tick={{ fill: '#666' }} />
          
          {/* User's current skills */}
          <Radar
            name="Your Skills"
            dataKey="userValue"
            stroke="#7D5BA6" // primary-purple color
            fill="#7D5BA6"
            fillOpacity={0.3}
            animationBegin={100}
            animationDuration={1000}
          />
          
          {/* Target career required skills */}
          <Radar
            name="Career Requirements"
            dataKey="careerValue"
            stroke="#59C2C9" // primary-teal color
            fill="#59C2C9"
            fillOpacity={0.3}
            animationBegin={300}
            animationDuration={1000}
          />
          
          <Tooltip content={<CustomTooltip />} />
        </RadarChart>
      </ResponsiveContainer>
      
      <div className="flex justify-center gap-6 mt-4">
        <div className="flex items-center">
          <div className="w-4 h-4 bg-primary-purple rounded-full mr-2"></div>
          <span className="text-sm text-gray-700">Your Current Skills</span>
        </div>
        <div className="flex items-center">
          <div className="w-4 h-4 bg-primary-teal rounded-full mr-2"></div>
          <span className="text-sm text-gray-700">Career Requirements</span>
        </div>
      </div>
      
      {/* Optional: Add career selection dropdown */}
      <div className="text-center mt-3">
        <select 
          value={selectedCareer}
          onChange={(e) => setSelectedCareer(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-teal"
        >
          <option value="Product Manager">Product Manager</option>
          <option value="Data Scientist">Data Scientist</option>
          <option value="UX Designer">UX Designer</option>
        </select>
      </div>
    </div>
  );
} 