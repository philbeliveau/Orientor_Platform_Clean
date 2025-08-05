/**
 * Program Details Modal Component
 * 
 * Displays detailed information about a program in a modal
 */

import React from 'react';
import { BookmarkPlus, ExternalLink, MapPin, GraduationCap, X } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Program } from './types';

interface ProgramDetailsProps {
  program: Program;
  onClose: () => void;
  onSave: (programId: string) => void;
}

const ProgramDetails: React.FC<ProgramDetailsProps> = ({ program, onClose, onSave }) => {
  const formatCurrency = (amount: number | undefined, currency: string = 'CAD') => {
    if (!amount) return 'N/A';
    return new Intl.NumberFormat('en-CA', { style: 'currency', currency }).format(amount);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-start mb-6">
            <div className="flex-1">
              <h1 className="text-3xl font-bold mb-2">{program.title}</h1>
              {program.title_fr && (
                <h2 className="text-xl text-muted-foreground mb-2">{program.title_fr}</h2>
              )}
              <div className="flex items-center gap-2 text-lg text-muted-foreground">
                <MapPin className="h-5 w-5" />
                <span>{program.institution.name}</span>
                <span>•</span>
                <span>{program.institution.city}, {program.institution.province}</span>
              </div>
            </div>
            <div className="flex gap-2">
              <Button onClick={() => onSave(program.id)}>
                <BookmarkPlus className="h-4 w-4 mr-2" />
                Save Program
              </Button>
              <Button variant="outline" onClick={onClose}>
                <X className="h-4 w-4 mr-2" />
                Close
              </Button>
            </div>
          </div>

          <Tabs defaultValue="overview" className="w-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="overview">Overview</TabsTrigger>
              <TabsTrigger value="admission">Admission</TabsTrigger>
              <TabsTrigger value="academics">Academics</TabsTrigger>
              <TabsTrigger value="careers">Careers</TabsTrigger>
            </TabsList>

            <TabsContent value="overview" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Program Details</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <span className="font-medium">Type:</span>
                      <span className="ml-2">{program.program_details.type}</span>
                    </div>
                    <div>
                      <span className="font-medium">Level:</span>
                      <span className="ml-2">{program.program_details.level}</span>
                    </div>
                    <div>
                      <span className="font-medium">Duration:</span>
                      <span className="ml-2">
                        {program.program_details.duration_months ? 
                          `${program.program_details.duration_months} months` : 'N/A'}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Languages:</span>
                      <span className="ml-2">{program.program_details.language.join(', ')}</span>
                    </div>
                    {program.program_details.cip_code && (
                      <div>
                        <span className="font-medium">CIP Code:</span>
                        <span className="ml-2">{program.program_details.cip_code}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Institution</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <span className="font-medium">Name:</span>
                      <span className="ml-2">{program.institution.name}</span>
                    </div>
                    <div>
                      <span className="font-medium">Type:</span>
                      <span className="ml-2">{program.institution.type}</span>
                    </div>
                    <div>
                      <span className="font-medium">Location:</span>
                      <span className="ml-2">{program.institution.city}, {program.institution.province}</span>
                    </div>
                    {program.institution.website && (
                      <div>
                        <a 
                          href={program.institution.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-1 text-blue-600 hover:underline"
                        >
                          <ExternalLink className="h-4 w-4" />
                          Visit Website
                        </a>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Costs</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div>
                      <span className="font-medium">Tuition (Domestic):</span>
                      <span className="ml-2">
                        {formatCurrency(program.costs.tuition_domestic, program.costs.currency)}
                      </span>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {program.description && (
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Description</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-muted-foreground">{program.description}</p>
                    {program.description_fr && (
                      <div className="mt-4">
                        <h4 className="font-medium mb-2">Description (Français):</h4>
                        <p className="text-muted-foreground">{program.description_fr}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="admission" className="space-y-6 mt-6">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Admission Requirements</CardTitle>
                </CardHeader>
                <CardContent>
                  {program.admission.requirements.length > 0 ? (
                    <ul className="list-disc list-inside space-y-2">
                      {program.admission.requirements.map((req, index) => (
                        <li key={index} className="text-muted-foreground">{req}</li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted-foreground">No specific requirements listed.</p>
                  )}
                  
                  {program.admission.deadline && (
                    <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                      <span className="font-medium">Application Deadline:</span>
                      <span className="ml-2">{program.admission.deadline}</span>
                    </div>
                  )}
                  
                  {program.admission.application_method && (
                    <div className="mt-4">
                      <span className="font-medium">Application Method:</span>
                      <span className="ml-2">{program.admission.application_method}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="academics" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Academic Structure</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {program.academic_info.credits && (
                      <div>
                        <span className="font-medium">Credits:</span>
                        <span className="ml-2">{program.academic_info.credits}</span>
                      </div>
                    )}
                    
                    <div className="space-y-2">
                      {program.academic_info.internship_required && (
                        <Badge variant="secondary">Internship Required</Badge>
                      )}
                      {program.academic_info.coop_available && (
                        <Badge variant="secondary">Co-op Available</Badge>
                      )}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Classification</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {program.classification.field_of_study && (
                      <div>
                        <span className="font-medium">Field of Study:</span>
                        <span className="ml-2">{program.classification.field_of_study}</span>
                      </div>
                    )}
                    {program.classification.category && (
                      <div>
                        <span className="font-medium">Category:</span>
                        <span className="ml-2">{program.classification.category}</span>
                      </div>
                    )}
                    {program.program_details.program_code && (
                      <div>
                        <span className="font-medium">Program Code:</span>
                        <span className="ml-2">{program.program_details.program_code}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            <TabsContent value="careers" className="space-y-6 mt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Career Outcomes</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {program.career_outcomes.employment_rate && (
                      <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                        <span className="font-medium">Employment Rate:</span>
                        <span className="ml-2 text-green-700 dark:text-green-400 font-bold">
                          {(program.career_outcomes.employment_rate * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                    
                    {program.career_outcomes.average_salary && (
                      <div>
                        <span className="font-medium">Average Salary Range:</span>
                        <div className="ml-2 text-muted-foreground">
                          {formatCurrency(program.career_outcomes.average_salary.min, program.career_outcomes.average_salary.currency)} - {' '}
                          {formatCurrency(program.career_outcomes.average_salary.max, program.career_outcomes.average_salary.currency)}
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-lg">Career Paths</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {program.career_outcomes.job_titles.length > 0 ? (
                      <ul className="space-y-2">
                        {program.career_outcomes.job_titles.map((title, index) => (
                          <li key={index} className="flex items-center gap-2">
                            <GraduationCap className="h-4 w-4 text-blue-600" />
                            <span>{title}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-muted-foreground">No career path information available.</p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
    </div>
  );
};

export default ProgramDetails;