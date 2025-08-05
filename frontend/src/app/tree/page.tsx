'use client';

import React from 'react';
import EnhancedSkillsTree from '@/components/tree/EnhancedSkillsTree';
import MainLayout from '@/components/layout/MainLayout';

// Page title and description
const title = 'Skill Tree Explorer';
const description = 'Discover your career path with our AI-powered skill tree generator';

export default function TreePage() {
  return (
    <MainLayout>
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-2">Skill Tree Explorer</h1>
        <p className="text-gray-600 mb-8">
          Enter your profile information to generate a personalized skill-to-career exploration map.
        </p>
        
        <EnhancedSkillsTree />
      </div>
    </MainLayout>
  );
} 