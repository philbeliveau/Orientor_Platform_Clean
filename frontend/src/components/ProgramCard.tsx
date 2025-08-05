import React from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { MapPin, Clock, DollarSign, TrendingUp, BookOpen, Users } from 'lucide-react';

interface ProgramCardProps {
  program: {
    id: string;
    title: string;
    title_fr?: string;
    institution_name: string;
    institution_city: string;
    program_type: string;
    level: string;
    duration_months?: number;
    tuition_domestic?: number;
    employment_rate?: number;
    holland_compatibility?: {
      score: number;
      codes: string[];
    };
    career_alignment_score?: number;
    skill_match_score?: number;
    recommendation_reasons?: string[];
  };
  onSave?: (programId: string) => void;
  onViewDetails?: (programId: string) => void;
  className?: string;
}

export function ProgramCard({ 
  program, 
  onSave, 
  onViewDetails, 
  className = '' 
}: ProgramCardProps) {
  const getCompatibilityColor = (score: number) => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'warning';
    return 'secondary';
  };

  const getCompatibilityText = (score: number) => {
    if (score >= 0.8) return 'Excellent Match';
    if (score >= 0.6) return 'Good Match';
    return 'Potential Match';
  };

  const formatTuition = (amount?: number) => {
    if (!amount) return 'Contact for pricing';
    return new Intl.NumberFormat('en-CA', {
      style: 'currency',
      currency: 'CAD',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDuration = (months?: number) => {
    if (!months) return 'Duration varies';
    const years = Math.floor(months / 12);
    const remainingMonths = months % 12;
    
    if (years === 0) return `${months} months`;
    if (remainingMonths === 0) return `${years} year${years > 1 ? 's' : ''}`;
    return `${years}y ${remainingMonths}m`;
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={className}
    >
      <Card className="h-full hover:shadow-lg transition-shadow duration-300 border-gray-200">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-start mb-2">
            <CardTitle className="text-lg font-semibold text-gray-900 line-clamp-2">
              {program.title}
            </CardTitle>
            {program.holland_compatibility && (
              <Badge variant={getCompatibilityColor(program.holland_compatibility.score)}>
                {Math.round(program.holland_compatibility.score * 100)}% Match
              </Badge>
            )}
          </div>
          
          <div className="flex items-center text-sm text-gray-600 mb-1">
            <BookOpen className="w-4 h-4 mr-1" />
            <span>{program.institution_name}</span>
          </div>
          
          <div className="flex items-center text-sm text-gray-500">
            <MapPin className="w-4 h-4 mr-1" />
            <span>{program.institution_city}</span>
            <span className="mx-2">•</span>
            <span className="capitalize">{program.level}</span>
          </div>
        </CardHeader>

        <CardContent className="pb-3">
          {/* Program Details */}
          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="flex items-center text-sm text-gray-600">
              <Clock className="w-4 h-4 mr-2 text-blue-500" />
              <span>{formatDuration(program.duration_months)}</span>
            </div>
            
            <div className="flex items-center text-sm text-gray-600">
              <DollarSign className="w-4 h-4 mr-2 text-green-500" />
              <span>{formatTuition(program.tuition_domestic)}</span>
            </div>
            
            {program.employment_rate && (
              <div className="flex items-center text-sm text-gray-600 col-span-2">
                <TrendingUp className="w-4 h-4 mr-2 text-purple-500" />
                <span>{Math.round(program.employment_rate * 100)}% employment rate</span>
              </div>
            )}
          </div>

          {/* Holland Compatibility Details */}
          {program.holland_compatibility && program.holland_compatibility.codes.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-1">Personality Match:</p>
              <div className="flex flex-wrap gap-1">
                {program.holland_compatibility.codes.map((code) => (
                  <Badge key={code} variant="outline" className="text-xs">
                    {code}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Recommendation Reasons */}
          {program.recommendation_reasons && program.recommendation_reasons.length > 0 && (
            <div className="mb-4">
              <p className="text-xs text-gray-500 mb-2">Why this matches you:</p>
              <ul className="text-sm text-gray-600 space-y-1">
                {program.recommendation_reasons.slice(0, 2).map((reason, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-500 mr-2">•</span>
                    <span className="line-clamp-1">{reason}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Program Type Badge */}
          <div className="flex items-center justify-between">
            <Badge variant="secondary" className="capitalize">
              {program.program_type}
            </Badge>
            
            {(program.career_alignment_score || program.skill_match_score) && (
              <div className="flex items-center text-xs text-gray-500">
                <Users className="w-3 h-3 mr-1" />
                <span>
                  {program.career_alignment_score && 
                    `${Math.round(program.career_alignment_score * 100)}% career fit`
                  }
                </span>
              </div>
            )}
          </div>
        </CardContent>

        <CardFooter className="flex gap-2 pt-3">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewDetails?.(program.id)}
            className="flex-1"
          >
            Learn More
          </Button>
          <Button
            size="sm"
            onClick={() => onSave?.(program.id)}
            className="flex-1 bg-blue-600 hover:bg-blue-700"
          >
            Save Program
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}