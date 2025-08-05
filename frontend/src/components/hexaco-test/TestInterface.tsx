'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HexacoQuestion, HexacoAnswerRequest } from '@/services/hexacoTestService';
import hexacoTestService from '@/services/hexacoTestService';

interface TestInterfaceProps {
  questions: HexacoQuestion[];
  sessionId: string;
  onTestComplete: (sessionId: string) => void;
  onError: (error: Error) => void;
}

const TestInterface: React.FC<TestInterfaceProps> = ({
  questions,
  sessionId,
  onTestComplete,
  onError,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [direction, setDirection] = useState(0); // -1: gauche, 1: droite
  const [isAnimating, setIsAnimating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [startTime, setStartTime] = useState<number>(Date.now());

  // Mettre à jour la progression
  useEffect(() => {
    setProgress((currentQuestionIndex / questions.length) * 100);
  }, [currentQuestionIndex, questions.length]);

  // Réinitialiser le temps de début pour chaque question
  useEffect(() => {
    setStartTime(Date.now());
  }, [currentQuestionIndex]);

  // Obtenir la question actuelle
  const currentQuestion = questions[currentQuestionIndex];

  // Gérer la sélection d'une réponse (échelle Likert 1-5)
  const handleResponseSelect = async (responseValue: number) => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    setDirection(-1); // Animation vers la gauche

    try {
      // Calculer le temps de réponse
      const responseTime = Date.now() - startTime;

      // Créer l'objet de réponse
      const answerData: HexacoAnswerRequest = {
        session_id: sessionId,
        item_id: currentQuestion.item_id,
        response_value: responseValue,
        response_time_ms: responseTime,
      };

      // Enregistrer la réponse via l'API
      await hexacoTestService.saveAnswer(answerData);

      // Attendre un court délai pour l'animation
      setTimeout(() => {
        // Passer à la question suivante ou terminer le test
        if (currentQuestionIndex < questions.length - 1) {
          setCurrentQuestionIndex(currentQuestionIndex + 1);
        } else {
          onTestComplete(sessionId);
        }
        setIsAnimating(false);
      }, 500);
    } catch (error) {
      setIsAnimating(false);
      onError(error as Error);
    }
  };

  // Variantes d'animation pour les questions
  const variants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 1000 : -1000,
      opacity: 0
    }),
    center: {
      x: 0,
      opacity: 1
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 1000 : -1000,
      opacity: 0
    })
  };

  // Options de réponse Likert (1-5)
  const likertOptions = [
    { value: 1, label: 'Fortement en désaccord', color: 'bg-red-500', hoverColor: 'hover:bg-red-600' },
    { value: 2, label: 'En désaccord', color: 'bg-orange-500', hoverColor: 'hover:bg-orange-600' },
    { value: 3, label: 'Neutre', color: 'bg-gray-500', hoverColor: 'hover:bg-gray-600' },
    { value: 4, label: 'D\'accord', color: 'bg-green-500', hoverColor: 'hover:bg-green-600' },
    { value: 5, label: 'Fortement d\'accord', color: 'bg-blue-500', hoverColor: 'hover:bg-blue-600' },
  ];

  // Si pas de questions, afficher un message de chargement
  if (!questions.length) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-lg">Chargement des questions...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900">
      {/* Barre de progression */}
      <div className="w-full bg-gray-200 dark:bg-gray-700 h-2">
        <div 
          className="bg-blue-600 h-2 transition-all duration-300 ease-out"
          style={{ width: `${progress}%` }}
        ></div>
      </div>
      
      {/* Compteur de questions */}
      <div className="p-4 text-center">
        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">
          Question {currentQuestionIndex + 1} sur {questions.length}
        </span>
      </div>

      {/* Zone de question */}
      <div className="flex-grow flex flex-col items-center justify-center px-4 md:px-8">
        <AnimatePresence initial={false} custom={direction} mode="wait">
          <motion.div
            key={currentQuestionIndex}
            custom={direction}
            variants={variants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{
              x: { type: "spring", stiffness: 300, damping: 30 },
              opacity: { duration: 0.2 }
            }}
            className="w-full max-w-4xl"
          >
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:p-8">
              {/* Informations sur la facette */}
              <div className="mb-4 text-center">
                <span className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 text-sm font-medium rounded-full">
                  {currentQuestion.facet}
                </span>
              </div>

              <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center text-gray-800 dark:text-white">
                {currentQuestion.item_text}
              </h2>
              
              {/* Échelle Likert */}
              <div className="space-y-3 mb-8">
                {likertOptions.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleResponseSelect(option.value)}
                    disabled={isAnimating}
                    className={`w-full p-4 text-left rounded-lg border-2 border-transparent ${option.color} ${option.hoverColor} text-white font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-105 active:scale-95`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-lg">
                        {option.label}
                      </span>
                      <span className="text-2xl font-bold">
                        {option.value}
                      </span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Indicateur de progression visuel */}
              <div className="flex justify-center space-x-2 mb-4">
                {Array.from({ length: Math.min(questions.length, 10) }).map((_, index) => {
                  const questionIndex = Math.floor((index / 10) * questions.length);
                  const isCompleted = questionIndex <= currentQuestionIndex;
                  const isCurrent = questionIndex === currentQuestionIndex;
                  
                  return (
                    <div
                      key={index}
                      className={`w-3 h-3 rounded-full transition-colors ${
                        isCurrent
                          ? 'bg-blue-600'
                          : isCompleted
                          ? 'bg-green-500'
                          : 'bg-gray-300 dark:bg-gray-600'
                      }`}
                    />
                  );
                })}
              </div>
              
              <div className="text-center text-sm text-gray-500 dark:text-gray-400">
                <p>Sélectionnez votre niveau d'accord avec cette affirmation</p>
                {currentQuestion.reverse_keyed && (
                  <p className="mt-1 text-xs text-orange-600 dark:text-orange-400">
                    ⚠️ Question à codage inversé
                  </p>
                )}
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default TestInterface;