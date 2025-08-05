'use client';

import React, { useRef, useState } from 'react';
import { motion, useScroll, useTransform, AnimatePresence } from 'framer-motion';
import { Container, Box, Typography, Button, Paper, Divider } from '@mui/material';
import MainLayout from '@/components/layout/MainLayout';
import DemoChat from '@/components/chat/DemoChat';
import JobSwipeCard from '@/components/chat/swipe_recommendation';
import CareerTree from '@/components/tree/CareerTree';
import EnhancedSkillsTree from '@/components/tree/EnhancedSkillsTree';
import SkillSpiderChart from '@/components/landing/SkillSpiderChart';

// Données fictives pour la visualisation d'école/programme
const schoolPrograms = [
  {
    id: 1,
    name: "Université de Montréal",
    program: "Informatique - Intelligence Artificielle",
    duration: "2 ans",
    cost: "8,500 € / an",
    skills: ["Machine Learning", "Deep Learning", "Python", "TensorFlow"],
    rating: 4.8,
  },
  {
    id: 2,
    name: "École Polytechnique",
    program: "Génie Logiciel",
    duration: "3 ans",
    cost: "7,800 € / an",
    skills: ["Développement Web", "Java", "Architecture Logicielle", "DevOps"],
    rating: 4.6,
  },
  {
    id: 3,
    name: "HEC Paris",
    program: "Management des Technologies",
    duration: "1 an",
    cost: "12,000 € / an",
    skills: ["Gestion de Projet", "Business Intelligence", "Leadership", "Innovation"],
    rating: 4.7,
  }
];

// Données fictives pour le constructeur de CV
const resumeTemplates = [
  { id: 1, name: "Professionnel", color: "#2c3e50" },
  { id: 2, name: "Créatif", color: "#8e44ad" },
  { id: 3, name: "Minimaliste", color: "#7f8c8d" },
];

export default function CaseStudyJourney() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: containerRef });
  const [selectedCareerPath, setSelectedCareerPath] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState(1);
  
  // Animation pour le défilement progressif
  const opacity = useTransform(scrollYProgress, [0, 0.2], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.2], [1, 0.8]);
  
  // Fonction pour naviguer vers une section spécifique
  const scrollToSection = (id: string) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  // Options de parcours de carrière
  const careerPaths = [
    { id: "data-science", name: "Data Science" },
    { id: "web-development", name: "Développement Web" },
    { id: "product-management", name: "Gestion de Produit" },
    { id: "ux-design", name: "UX Design" }
  ];

  return (
    <MainLayout>
      <div ref={containerRef} className="min-h-screen">
        {/* Section d'introduction avec animation */}
        <motion.div 
          className="h-screen flex items-center justify-center bg-gradient-to-b from-blue-50 to-white"
          style={{ opacity, scale }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8 }}
        >
          <Container maxWidth="md">
            <Typography variant="h2" component="h1" align="center" gutterBottom className="font-bold text-gray-800">
              Étude de Cas Navigo
            </Typography>
            <Typography variant="h5" align="center" color="textSecondary" paragraph>
              Découvrez votre parcours professionnel idéal à travers une expérience interactive guidée
            </Typography>
            <Box mt={4} display="flex" justifyContent="center">
              <Button 
                variant="contained" 
                color="primary" 
                size="large"
                onClick={() => scrollToSection('chat-section')}
                className="bg-blue-600 hover:bg-blue-700"
              >
                Commencer l'expérience
              </Button>
            </Box>
          </Container>
        </motion.div>

        {/* Section 1: Conversation LLM avec bulles de chat */}
        <section id="chat-section" className="min-h-screen py-16 bg-white">
          <Container maxWidth="md">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Discutez avec votre conseiller d'orientation IA
              </Typography>
              <DemoChat />
              <Box mt={4} display="flex" justifyContent="center">
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => scrollToSection('job-recommendations')}
                  className="mt-8"
                >
                  Découvrir les recommandations de carrière
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>

        {/* Section 2: Recommandations de cartes à faire défiler */}
        <section id="job-recommendations" className="min-h-screen py-16 bg-gray-50">
          <Container maxWidth="md">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Explorez les carrières recommandées
              </Typography>
              <JobSwipeCard />
              <Box mt={4} display="flex" justifyContent="center">
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => scrollToSection('career-tree')}
                  className="mt-8"
                >
                  Explorer l'arbre de carrière
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>

        {/* Section 3: Arbre de carrière interactif */}
        <section id="career-tree" className="min-h-screen py-16 bg-white">
          <Container maxWidth="lg">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Visualisez votre arbre de carrière
              </Typography>
              <div className="h-[600px] w-full">
                <CareerTree />
              </div>
              <Box mt={4} display="flex" justifyContent="center">
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => scrollToSection('career-path-selection')}
                  className="mt-8"
                >
                  Sélectionner un parcours de carrière
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>

        {/* Section 4: Sélection de parcours de carrière spécifique */}
        <section id="career-path-selection" className="min-h-screen py-16 bg-gray-50">
          <Container maxWidth="md">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Choisissez votre parcours de carrière
              </Typography>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {careerPaths.map((path) => (
                  <motion.div
                    key={path.id}
                    whileHover={{ scale: 1.03 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Paper 
                      className={`p-6 cursor-pointer transition-all ${selectedCareerPath === path.id ? 'border-2 border-blue-500 shadow-lg' : 'border border-gray-200'}`}
                      onClick={() => setSelectedCareerPath(path.id)}
                      elevation={selectedCareerPath === path.id ? 4 : 1}
                    >
                      <Typography variant="h6" component="h3" gutterBottom>
                        {path.name}
                      </Typography>
                      <Typography variant="body2" color="textSecondary">
                        Explorez les compétences, formations et opportunités dans le domaine {path.name.toLowerCase()}.
                      </Typography>
                      {selectedCareerPath === path.id && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          className="mt-3 text-blue-600 font-medium"
                        >
                          ✓ Sélectionné
                        </motion.div>
                      )}
                    </Paper>
                  </motion.div>
                ))}
              </div>
              
              <Box mt={6} display="flex" justifyContent="center">
                <Button 
                  variant="contained" 
                  color="primary"
                  disabled={!selectedCareerPath}
                  onClick={() => scrollToSection('skills-tree')}
                  className="mt-4 bg-blue-600 hover:bg-blue-700"
                >
                  Voir l'arbre de compétences
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>

        {/* Section 5: Arbre de compétences */}
        <section id="skills-tree" className="min-h-screen py-16 bg-white">
          <Container maxWidth="lg">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Développez vos compétences
              </Typography>
              <div className="h-[600px] w-full">
                <EnhancedSkillsTree />
              </div>
              <Box mt={4} display="flex" justifyContent="center">
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => scrollToSection('skill-comparison')}
                  className="mt-8"
                >
                  Comparer vos compétences
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>

        {/* Section 6: Graphique de comparaison de compétences */}
        <section id="skill-comparison" className="min-h-screen py-16 bg-gray-50">
          <Container maxWidth="md">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Comparez vos compétences avec les exigences du marché
              </Typography>
              <Paper className="p-6">
                <SkillSpiderChart />
              </Paper>
              <Box mt={4} display="flex" justifyContent="center">
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => scrollToSection('school-programs')}
                  className="mt-8"
                >
                  Découvrir les programmes de formation
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>

        {/* Section 7: Visualisation d'école/programme */}
        <section id="school-programs" className="min-h-screen py-16 bg-white">
          <Container maxWidth="md">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Programmes de formation recommandés
              </Typography>
              
              <div className="space-y-6">
                {schoolPrograms.map((program) => (
                  <motion.div
                    key={program.id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Paper className="p-6">
                      <div className="flex justify-between items-start">
                        <div>
                          <Typography variant="h6" component="h3" gutterBottom>
                            {program.name}
                          </Typography>
                          <Typography variant="subtitle1" color="primary" gutterBottom>
                            {program.program}
                          </Typography>
                        </div>
                        <div className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">
                          {program.rating}/5
                        </div>
                      </div>
                      
                      <Divider className="my-3" />
                      
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                        <div>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            <strong>Durée:</strong> {program.duration}
                          </Typography>
                          <Typography variant="body2" color="textSecondary">
                            <strong>Coût:</strong> {program.cost}
                          </Typography>
                        </div>
                        <div>
                          <Typography variant="body2" color="textSecondary" gutterBottom>
                            <strong>Compétences acquises:</strong>
                          </Typography>
                          <div className="flex flex-wrap gap-2 mt-1">
                            {program.skills.map((skill, index) => (
                              <span key={index} className="bg-gray-100 px-2 py-1 rounded-md text-xs">
                                {skill}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                      
                      <Button 
                        variant="outlined" 
                        color="primary" 
                        size="small" 
                        className="mt-4"
                      >
                        En savoir plus
                      </Button>
                    </Paper>
                  </motion.div>
                ))}
              </div>
              
              <Box mt={4} display="flex" justifyContent="center">
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => scrollToSection('resume-builder')}
                  className="mt-8"
                >
                  Créer votre CV
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>

        {/* Section 8: Constructeur de CV */}
        <section id="resume-builder" className="min-h-screen py-16 bg-gray-50">
          <Container maxWidth="md">
            <motion.div
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
            >
              <Typography variant="h4" component="h2" align="center" gutterBottom className="mb-8 font-semibold text-gray-800">
                Créez votre CV professionnel
              </Typography>
              
              <Paper className="p-6">
                <Typography variant="h6" gutterBottom>
                  Choisissez un modèle
                </Typography>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  {resumeTemplates.map((template) => (
                    <motion.div
                      key={template.id}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Paper 
                        className={`p-4 cursor-pointer transition-all ${selectedTemplate === template.id ? 'border-2 border-blue-500' : 'border border-gray-200'}`}
                        onClick={() => setSelectedTemplate(template.id)}
                        elevation={selectedTemplate === template.id ? 3 : 1}
                      >
                        <div 
                          className="h-40 mb-3 rounded-md" 
                          style={{ backgroundColor: template.color }}
                        />
                        <Typography variant="body1" align="center">
                          {template.name}
                        </Typography>
                      </Paper>
                    </motion.div>
                  ))}
                </div>
                
                <Box mt={6}>
                  <Typography variant="h6" gutterBottom>
                    Vos informations sont prêtes à être intégrées
                  </Typography>
                  <Typography variant="body2" paragraph>
                    Basé sur votre parcours et vos compétences, nous avons préparé un CV adapté à votre profil et au domaine {selectedCareerPath ? careerPaths.find(p => p.id === selectedCareerPath)?.name.toLowerCase() : "sélectionné"}.
                  </Typography>
                  
                  <div className="bg-gray-100 p-4 rounded-md mt-4">
                    <Typography variant="body2" component="div">
                      <ul className="list-disc pl-5 space-y-1">
                        <li>Vos compétences techniques et transversales</li>
                        <li>Votre parcours de formation recommandé</li>
                        <li>Projets suggérés pour renforcer votre profil</li>
                        <li>Mots-clés optimisés pour les ATS (systèmes de suivi des candidatures)</li>
                      </ul>
                    </Typography>
                  </div>
                </Box>
                
                <Box mt={4} display="flex" justifyContent="center">
                  <Button 
                    variant="contained" 
                    color="primary"
                    className="mt-4 bg-blue-600 hover:bg-blue-700"
                  >
                    Générer mon CV
                  </Button>
                </Box>
              </Paper>
              
              <Box mt={8} display="flex" justifyContent="center">
                <Button 
                  variant="outlined" 
                  color="primary"
                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                >
                  Retour au début
                </Button>
              </Box>
            </motion.div>
          </Container>
        </section>
      </div>
    </MainLayout>
  );
}