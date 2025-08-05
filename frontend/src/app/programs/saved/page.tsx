/**
 * Saved Programs Page
 * 
 * Display and manage user's saved programs
 */

'use client';

import React, { useState, useEffect } from 'react';
import { BookmarkIcon, Trash2, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'react-hot-toast';
import { schoolProgramsService } from '@/services/schoolProgramsService';
import { Program } from '@/components/school-programs/types';

export default function SavedProgramsPage() {
  const [savedPrograms, setSavedPrograms] = useState<Program[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadSavedPrograms();
  }, []);

  const loadSavedPrograms = async () => {
    try {
      setIsLoading(true);
      const programs = await schoolProgramsService.getSavedPrograms();
      setSavedPrograms(programs);
    } catch (error) {
      toast.error("Failed to load saved programs.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveProgram = async (programId: string) => {
    try {
      await schoolProgramsService.removeSavedProgram(programId);
      setSavedPrograms(prev => prev.filter(p => p.id !== programId));
      toast.success("Program removed from your saved list.");
    } catch (error) {
      toast.error("Failed to remove program.");
    }
  };

  const formatCurrency = (amount: number | undefined, currency: string = 'CAD') => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-CA', { style: 'currency', currency }).format(amount);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="flex justify-center items-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <div className="flex items-center gap-2 mb-4">
          <BookmarkIcon className="h-6 w-6" />
          <h1 className="text-3xl font-bold">Saved Programs</h1>
        </div>
        <p className="text-muted-foreground">
          Manage your saved programs and track your application progress.
        </p>
      </div>

      {savedPrograms.length === 0 ? (
        <Card className="text-center py-12">
          <CardContent>
            <BookmarkIcon className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No Saved Programs</h3>
            <p className="text-muted-foreground mb-4">
              Start exploring programs and save the ones that interest you.
            </p>
            <Button onClick={() => window.location.href = '/programs'}>
              Search Programs
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedPrograms.map((program) => (
            <Card key={program.id} className="h-full">
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <CardTitle className="text-lg mb-2 line-clamp-2">
                      {program.title}
                    </CardTitle>
                    <p className="text-sm text-muted-foreground mb-2">
                      {program.institution.name}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {program.institution.city}, {program.institution.province}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleRemoveProgram(program.id)}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex gap-2 flex-wrap">
                    <Badge variant="secondary">
                      {program.program_details.type}
                    </Badge>
                    <Badge variant="outline">
                      {program.program_details.level}
                    </Badge>
                  </div>

                  {program.program_details.duration_months && (
                    <div className="text-sm">
                      <span className="font-medium">Duration:</span>
                      <span className="ml-2">
                        {program.program_details.duration_months} months
                      </span>
                    </div>
                  )}

                  {program.costs.tuition_domestic && (
                    <div className="text-sm">
                      <span className="font-medium">Tuition:</span>
                      <span className="ml-2">
                        {formatCurrency(program.costs.tuition_domestic, program.costs.currency)}
                      </span>
                    </div>
                  )}

                  {program.career_outcomes.employment_rate && (
                    <div className="text-sm">
                      <span className="font-medium">Employment Rate:</span>
                      <span className="ml-2 text-green-600 font-medium">
                        {(program.career_outcomes.employment_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                  )}

                  <div className="flex gap-2 mt-4">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="flex-1"
                      onClick={() => window.location.href = `/programs/${program.id}`}
                    >
                      View Details
                    </Button>
                    {program.institution.website && (
                      <Button 
                        variant="outline" 
                        size="sm"
                        onClick={() => window.open(program.institution.website, '_blank', 'noopener,noreferrer')}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}