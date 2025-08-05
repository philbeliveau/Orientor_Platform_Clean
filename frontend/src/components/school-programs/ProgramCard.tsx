/**
 * Program Card Component
 * 
 * Displays a program in a card format with key information and actions
 */

import React from 'react';
import { BookmarkPlus, MapPin, Clock, DollarSign } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Program } from './types';

interface ProgramCardProps {
  program: Program;
  onSave: (programId: string) => void;
  onView: (programId: string) => void;
}

const ProgramCard: React.FC<ProgramCardProps> = ({ program, onSave, onView }) => {
  const formatCurrency = (amount: number | undefined, currency: string = 'CAD') => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-CA', { style: 'currency', currency }).format(amount);
  };

  const formatDuration = (months: number | undefined) => {
    if (!months) return 'N/A';
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    if (years > 0 && remainingMonths > 0) {
      return `${years}y ${remainingMonths}m`;
    } else if (years > 0) {
      return `${years} year${years > 1 ? 's' : ''}`;
    } else {
      return `${months} month${months > 1 ? 's' : ''}`;
    }
  };

  return (
    <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer group">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex-1">
            <CardTitle 
              className="text-lg mb-2 line-clamp-2 group-hover:text-primary transition-colors" 
              onClick={() => onView(program.id)}
            >
              {program.title}
            </CardTitle>
            <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
              <MapPin className="h-4 w-4" />
              <span>{program.institution.name}</span>
              <span>•</span>
              <span>{program.institution.city}, {program.institution.province}</span>
            </div>
            <div className="flex gap-2 mb-3 flex-wrap">
              <Badge variant="secondary">
                {program.program_details.type}
              </Badge>
              <Badge variant="outline">
                {program.program_details.level}
              </Badge>
              {program.institution.type && (
                <Badge variant="outline">
                  {program.institution.type.toUpperCase()}
                </Badge>
              )}
            </div>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={(e) => {
              e.stopPropagation();
              onSave(program.id);
            }}
            className="shrink-0"
          >
            <BookmarkPlus className="h-4 w-4" />
          </Button>
        </div>
      </CardHeader>
      <CardContent onClick={() => onView(program.id)}>
        {program.description && (
          <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
            {program.description}
          </p>
        )}
        
        <div className="space-y-3">
          {/* Duration and Cost */}
          <div className="flex justify-between items-center text-sm">
            <div className="flex items-center gap-1">
              <Clock className="h-4 w-4" />
              <span>{formatDuration(program.program_details.duration_months)}</span>
            </div>
            <div className="flex items-center gap-1">
              <DollarSign className="h-4 w-4" />
              <span>{formatCurrency(program.costs.tuition_domestic, program.costs.currency)}</span>
            </div>
          </div>

          {/* Employment Rate */}
          {program.career_outcomes.employment_rate && (
            <div className="flex items-center justify-between text-sm">
              <span>Employment Rate:</span>
              <span className="font-medium text-green-600">
                {(program.career_outcomes.employment_rate * 100).toFixed(0)}%
              </span>
            </div>
          )}

          {/* Languages */}
          <div className="flex items-center gap-2">
            <span className="text-sm">Languages:</span>
            <div className="flex gap-1">
              {program.program_details.language.map((lang) => (
                <Badge key={lang} variant="outline" className="text-xs">
                  {lang.toUpperCase()}
                </Badge>
              ))}
            </div>
          </div>

          {/* Special Features */}
          <div className="flex gap-2 flex-wrap">
            {program.academic_info.internship_required && (
              <Badge variant="secondary" className="text-xs">Internship Required</Badge>
            )}
            {program.academic_info.coop_available && (
              <Badge variant="secondary" className="text-xs">Co-op Available</Badge>
            )}
          </div>

          {/* Career Outcomes */}
          {program.career_outcomes.job_titles.length > 0 && (
            <div className="text-sm">
              <span className="font-medium">Career Paths:</span>
              <p className="text-muted-foreground mt-1">
                {program.career_outcomes.job_titles.slice(0, 3).join(', ')}
                {program.career_outcomes.job_titles.length > 3 && '...'}
              </p>
            </div>
          )}

          {/* Field of Study */}
          {program.classification.field_of_study && (
            <div className="text-sm">
              <span className="font-medium">Field:</span>
              <span className="text-muted-foreground ml-1">
                {program.classification.field_of_study}
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default ProgramCard;