'use client';
import React, { useState } from 'react';
import MainLayout from '@/components/layout/MainLayout';
import UserCard from '@/components/ui/UserCard';
import ChallengeCard from '@/components/ui/ChallengeCard';
import StyledTreeGraph from '@/components/ui/StyledTreeGraph';
import { Node, Edge } from 'reactflow';
import { motion } from 'framer-motion';

export default function StitchDemoPage() {
  // Données d'exemple pour les utilisateurs
  const users = [
    {
      name: 'Philippe B.',
      role: 'Msc. in Data Science',
      avatarUrl: '/Users/philippebeliveau/Desktop/Notebook/Orientor_project/Orientor_project/frontend/public/Avatar.PNG',
      skills: ['UI Design', 'Wireframing', 'User Research'],
      domain: 'communicator' as const
    },
    {
      name: 'Thomas Dubois',
      role: 'Full Stack Developer',
      avatarUrl: 'https://randomuser.me/api/portraits/men/32.jpg',
      skills: ['React', 'Node.js', 'TypeScript', 'MongoDB'],
      domain: 'builder' as const
    },
    {
      name: 'Emma Leclerc',
      role: 'Data Scientist',
      avatarUrl: 'https://randomuser.me/api/portraits/women/68.jpg',
      skills: ['Python', 'Machine Learning', 'Data Visualization'],
      domain: undefined
    }
  ];

  // Données d'exemple pour les défis
  const challenges = [
    {
      title: 'Apprendre React Flow',
      description: 'Créez un graphe interactif avec React Flow et intégrez-le dans un projet existant.',
      xpReward: 150,
      progress: 75,
      isCompleted: false,
      difficulty: 'medium' as const,
      domain: 'builder' as const
    },
    {
      title: 'Maîtriser Framer Motion',
      description: 'Implémentez des animations complexes avec Framer Motion pour améliorer l\'expérience utilisateur.',
      xpReward: 200,
      progress: 30,
      isCompleted: false,
      difficulty: 'hard' as const,
      domain: 'builder' as const
    },
    {
      title: 'Présentation de projet',
      description: 'Préparez et délivrez une présentation de 10 minutes sur votre dernier projet à l\'équipe.',
      xpReward: 100,
      progress: 100,
      isCompleted: true,
      difficulty: 'easy' as const,
      domain: 'communicator' as const
    }
  ];

  // Données d'exemple pour le graphe
  const initialNodes: Node[] = [
    {
      id: '1',
      type: 'custom',
      position: { x: 250, y: 0 },
      data: { 
        label: 'Frontend Development', 
        description: 'Compétences et technologies pour le développement frontend.',
        expandable: true,
        active: true,
        skills: ['HTML', 'CSS', 'JavaScript']
      }
    },
    {
      id: '2',
      type: 'custom',
      position: { x: 100, y: 150 },
      data: { 
        label: 'React', 
        description: 'Bibliothèque JavaScript pour construire des interfaces utilisateur.',
        expandable: true,
        skills: ['JSX', 'Hooks', 'Context API']
      }
    },
    {
      id: '3',
      type: 'custom',
      position: { x: 400, y: 150 },
      data: { 
        label: 'CSS Avancé', 
        description: 'Techniques avancées de mise en page et de style.',
        expandable: true,
        skills: ['Flexbox', 'Grid', 'Animations']
      }
    },
    {
      id: '4',
      type: 'custom',
      position: { x: 100, y: 300 },
      data: { 
        label: 'Next.js', 
        description: 'Framework React pour la production.',
        expandable: true,
        skills: ['SSR', 'File-based Routing', 'API Routes']
      }
    }
  ];

  const initialEdges: Edge[] = [
    { id: 'e1-2', source: '1', target: '2', className: 'tree-edge' },
    { id: 'e1-3', source: '1', target: '3', className: 'tree-edge' },
    { id: 'e2-4', source: '2', target: '4', className: 'tree-edge' }
  ];

  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  return (
    <MainLayout>
      <div className="bg-stitch-pattern min-h-screen">
        <div className="layout-container py-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="text-4xl font-bold font-departure text-stitch-accent mb-8">
              Stitch Design System
            </h1>
            
            <p className="text-stitch-sage mb-12">
              Une démonstration du thème UI "Stitch Design" avec ses composants et styles.
            </p>

            {/* Section des couleurs */}
            <section className="mb-16">
              <h2 className="text-2xl font-bold font-departure text-stitch-accent mb-6">
                Palette de couleurs
              </h2>
              
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-lg bg-stitch-primary border border-stitch-border"></div>
                  <span className="text-sm text-stitch-sage mt-2">#122112</span>
                  <span className="text-xs text-stitch-sage">Primary BG</span>
                </div>
                
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-lg bg-stitch-accent border border-stitch-border"></div>
                  <span className="text-sm text-stitch-sage mt-2">#19b219</span>
                  <span className="text-xs text-stitch-sage">Accent Green</span>
                </div>
                
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-lg bg-stitch-sage border border-stitch-border"></div>
                  <span className="text-sm text-stitch-sage mt-2">#95c695</span>
                  <span className="text-xs text-stitch-sage">Sage Text</span>
                </div>
                
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-lg bg-stitch-border border border-stitch-border"></div>
                  <span className="text-sm text-stitch-sage mt-2">#254625</span>
                  <span className="text-xs text-stitch-sage">Border Green</span>
                </div>
                
                <div className="flex flex-col items-center">
                  <div className="w-20 h-20 rounded-lg bg-stitch-track border border-stitch-border"></div>
                  <span className="text-sm text-stitch-sage mt-2">#366336</span>
                  <span className="text-xs text-stitch-sage">Progress Track</span>
                </div>
              </div>
            </section>

            {/* Section de typographie */}
            <section className="mb-16">
              <h2 className="text-2xl font-bold font-departure text-stitch-accent mb-6">
                Typographie
              </h2>
              
              <div className="grid gap-6">
                <div>
                  <h1 className="text-4xl font-bold text-stitch-accent">Heading 1</h1>
                  <p className="text-xs text-stitch-sage mt-1">Font: inter, Bold, 2.25rem</p>
                </div>
                
                <div>
                  <h2 className="text-3xl font-bold text-stitch-accent">Heading 2</h2>
                  <p className="text-xs text-stitch-sage mt-1">Font: inter, Bold, 1.875rem</p>
                </div>
                
                <div>
                  <h3 className="text-2xl font-bold text-stitch-accent">Heading 3</h3>
                  <p className="text-xs text-stitch-sage mt-1">Font: inter, Bold, 1.5rem</p>
                </div>
                
                <div>
                  <p className="text-stitch-sage">Texte de paragraphe standard en Noto Sans. Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam in dui mauris. Vivamus hendrerit arcu sed erat molestie vehicula.</p>
                  <p className="text-xs text-stitch-sage mt-1">Font: Noto Sans, Regular, 1rem</p>
                </div>
              </div>
            </section>

            {/* Section des composants */}
            <section className="mb-16">
              <h2 className="text-2xl font-bold font-departure text-stitch-accent mb-6">
                Composants UI
              </h2>
              
              {/* Boutons */}
              <div className="mb-10">
                <h3 className="text-xl font-bold font-departure text-stitch-accent mb-4">Boutons</h3>
                <div className="flex flex-wrap gap-4">
                  <button className="btn btn-primary">Bouton Primaire</button>
                  <button className="btn btn-secondary">Bouton Secondaire</button>
                  <button className="btn btn-ghost">Bouton Ghost</button>
                  <button className="btn btn-builder">Bouton Builder</button>
                  <button className="btn btn-communicator">Bouton Communicator</button>
                </div>
              </div>
              
              {/* Barres de progression */}
              <div className="mb-10">
                <h3 className="text-xl font-bold font-departure text-stitch-accent mb-4">Barres de progression</h3>
                <div className="space-y-6 max-w-md">
                  <div>
                    <div className="flex justify-between text-sm text-stitch-sage mb-1">
                      <span>Progression 25%</span>
                      <span>25/100</span>
                    </div>
                    <div className="progress-container">
                      <div className="progress-fill" style={{ width: '25%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm text-stitch-sage mb-1">
                      <span>Progression 50%</span>
                      <span>50/100</span>
                    </div>
                    <div className="progress-container">
                      <div className="progress-fill" style={{ width: '50%' }}></div>
                    </div>
                  </div>
                  
                  <div>
                    <div className="flex justify-between text-sm text-stitch-sage mb-1">
                      <span>Progression 75%</span>
                      <span>75/100</span>
                    </div>
                    <div className="progress-container">
                      <div className="progress-fill" style={{ width: '75%' }}></div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Cartes utilisateur */}
              <div className="mb-10">
                <h3 className="text-xl font-bold font-departure text-stitch-accent mb-4">Cartes utilisateur</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {users.map((user, index) => (
                    <UserCard
                      key={index}
                      name={user.name}
                      role={user.role}
                      skills={user.skills}
                    />
                  ))}
                </div>
              </div>
              
              {/* Cartes de défi */}
              <div className="mb-10">
                <h3 className="text-xl font-bold font-departure text-stitch-accent mb-4">Cartes de défi</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  {challenges.map((challenge, index) => (
                    <ChallengeCard
                      key={index}
                      challenge={challenge.title}
                      xpReward={challenge.xpReward}
                      completed={challenge.isCompleted}
                      onComplete={() => console.log('Challenge completed:', challenge.title)}
                    />
                  ))}
                </div>
              </div>
              
              {/* Graphe d'arbre */}
              <div className="mb-10">
                <h3 className="text-xl font-bold font-departure text-stitch-accent mb-4">Graphe d'arbre</h3>
                <div className="border border-stitch-border rounded-xl overflow-hidden">
                  <StyledTreeGraph
                    nodes={nodes}
                    edges={edges}
                    className="h-[600px]"
                  />
                </div>
              </div>
            </section>
          </motion.div>
        </div>
      </div>
    </MainLayout>
  );
}