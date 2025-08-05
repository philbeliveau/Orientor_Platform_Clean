'use client';

import React from 'react';
import { CompetenceTreeView } from '@/features/skills';
import { LazyWrapper } from '@/features/shared/components/LazyWrapper';

export default function TreePage() {
  // This is an example of how to refactor the tree page to use the new modular components
  // The CompetenceTreeView is now lazy loaded and split into smaller components
  
  const graphId = 'default'; // Would get from context or params
  
  return (
    <LazyWrapper>
      <div className="h-screen w-full">
        <CompetenceTreeView graphId={graphId} />
      </div>
    </LazyWrapper>
  );
}