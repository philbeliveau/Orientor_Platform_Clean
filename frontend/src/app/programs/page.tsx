/**
 * School Programs Search Page
 * 
 * Main page for searching and discovering CEGEP and university programs
 */

import React from 'react';
import SchoolProgramsSearch from '@/components/school-programs/SchoolProgramsSearch';

export default function ProgramsPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-4">Find Your Perfect Program</h1>
          <p className="text-xl text-muted-foreground">
            Discover CEGEP and university programs that match your interests, personality, and career goals.
          </p>
        </div>
        
        <SchoolProgramsSearch />
      </div>
    </div>
  );
}