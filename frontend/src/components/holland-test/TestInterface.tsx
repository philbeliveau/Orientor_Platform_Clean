'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Question, AnswerRequest } from '@/services/hollandTestService';
import hollandTestService from '@/services/hollandTestService';
import { useSwipeable } from 'react-swipeable';

interface TestinterfaceProps {
  questions: Question[];
  attemptId: string;
  onTestComplete: (attemptId: string) => void;
  onError: (error: Error) => void;
}

const Testinterface: React.FC<TestinterfaceProps> = ({
  questions,
  attemptId,
  onTestComplete,
  onError,
}) => {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [direction, setDirection] = useState(0); // -1: gauche, 1: droite
  const [isAnimating, setIsAnimating] = useState(false);
  const [progress, setProgress] = useState(0);

  // Mettre à jour la progression
  useEffect(() => {
    setProgress((currentQuestionIndex / questions.length) * 100);
  }, [currentQuestionIndex, questions.length]);

  // Obtenir la question actuelle
  const currentQuestion = questions[currentQuestionIndex];

  // Gérer la sélection d'une réponse
  const handleChoiceSelect = async (choiceId: number) => {
    if (isAnimating) return;
    
    setIsAnimating(true);
    setDirection(-1); // Animation vers la gauche

    try {
      // Créer l'objet de réponse
      const answerData: AnswerRequest = {
        attempt_id: attemptId,
        question_id: currentQuestion.id,
        choice_id: choiceId,
      };

      // Enregistrer la réponse via l'API
      await hollandTestService.saveAnswer(answerData);

      // Attendre un court délai pour l'animation
      setTimeout(() => {
        // Passer à la question suivante ou terminer le test
        if (currentQuestionIndex < questions.length - 1) {
          setCurrentQuestionIndex(currentQuestionIndex + 1);
        } else {
          onTestComplete(attemptId);
        }
        setIsAnimating(false);
      }, 500);
    } catch (error) {
      setIsAnimating(false);
      onError(error as Error);
    }
  };

  // Configuration des gestionnaires de balayage
  const swipeHandlers = useSwipeable({
    onSwipedLeft: () => {
      if (isAnimating || !currentQuestion) return;
      if (currentQuestion.choices.length > 0) {
        handleChoiceSelect(currentQuestion.choices[0].id);
      }
    },
    onSwipedRight: () => {
      if (isAnimating || !currentQuestion) return;
      if (currentQuestion.choices.length > 0) {
        handleChoiceSelect(currentQuestion.choices[currentQuestion.choices.length - 1].id);
      }
    },
    trackMouse: true
  });

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
    <div className="flex flex-col h-screen bg-gray-50 dark:bg-gray-900" {...swipeHandlers}>
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
            className="w-full max-w-3xl"
          >
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 md:p-8">
              <h2 className="text-2xl md:text-3xl font-bold mb-8 text-center text-gray-800 dark:text-white">
                {currentQuestion.title}
              </h2>
              
              <div className="space-y-4">
                {currentQuestion.choices.map((choice) => (
                  <button
                    key={choice.id}
                    onClick={() => handleChoiceSelect(choice.id)}
                    disabled={isAnimating}
                    className="w-full p-4 text-left rounded-lg border-2 border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="text-lg text-gray-800 dark:text-gray-200">
                      {choice.title}
                    </span>
                  </button>
                ))}
              </div>
              
              <div className="mt-8 text-center text-sm text-gray-500 dark:text-gray-400">
                <p>Balayez vers la gauche ou cliquez sur une option pour continuer</p>
              </div>
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Testinterface;