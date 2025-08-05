'use client';
import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { MessageCircle, Lightbulb, ArrowRight } from 'lucide-react';

interface ColorfulDailyQuestionCardProps {
  userId?: number;
  style?: React.CSSProperties;
  className?: string;
}

const dailyQuestions = [
  "Qu'est-ce qui vous motive le plus dans votre parcours professionnel actuel ?",
  "Si vous pouviez changer une chose dans votre approche d'apprentissage, que serait-ce ?",
  "Quelle compétence aimeriez-vous développer cette semaine et pourquoi ?",
  "Comment définissez-vous le succès dans votre domaine d'études ?",
  "Quel conseil donneriez-vous à quelqu'un qui commence dans votre domaine ?",
  "Quelle est la plus grande leçon que vous avez apprise récemment ?",
  "Comment équilibrez-vous vos objectifs à court et long terme ?",
  "Qu'est-ce qui vous inspire le plus dans votre domaine d'études ?",
  "Comment gérez-vous les défis et les obstacles dans votre apprentissage ?",
  "Quelle habitude pourriez-vous adopter pour améliorer votre productivité ?",
];

const ColorfulDailyQuestionCard: React.FC<ColorfulDailyQuestionCardProps> = ({ 
  userId = 1, 
  style, 
  className = '' 
}) => {
  const router = useRouter();
  const [question, setQuestion] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(true);
  
  useEffect(() => {
    // Generate a "daily" question based on the current date
    const today = new Date();
    const dayOfYear = Math.floor((today.getTime() - new Date(today.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
    const questionIndex = dayOfYear % dailyQuestions.length;
    
    setTimeout(() => {
      setQuestion(dailyQuestions[questionIndex]);
      setLoading(false);
    }, 500);
  }, [userId]);
  
  const handleClick = () => {
    // Navigate to chat with the question as initial message
    const encodedQuestion = encodeURIComponent(question);
    router.push(`/chat?initial_message=${encodedQuestion}&type=daily_reflection`);
  };

  return (
    <div 
      className={`bg-gradient-to-br from-purple-500 to-purple-600 rounded-3xl p-4 sm:p-6 shadow-lg hover:shadow-xl active:scale-95 transition-all duration-300 cursor-pointer group relative overflow-hidden touch-none select-none ${className}`}
      style={{
        minHeight: '200px',
        WebkitTapHighlightColor: 'transparent',
        touchAction: 'manipulation',
        ...style
      }}
      onClick={handleClick}
    >
      {/* Background decoration */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full -translate-y-16 translate-x-16"></div>
      <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
      
      {/* Header */}
      <div className="flex items-center justify-between mb-3 sm:mb-4 relative z-10">
        <div className="flex items-center gap-2 sm:gap-3">
          <div className="w-8 h-8 sm:w-10 sm:h-10 bg-white/20 rounded-xl sm:rounded-2xl flex items-center justify-center backdrop-blur-sm">
            <Lightbulb className="w-4 h-4 sm:w-5 sm:h-5 text-white" />
          </div>
          <div>
            <h3 className="text-base sm:text-lg font-semibold text-white">Question du Jour</h3>
            <p className="text-purple-100 text-xs sm:text-sm">Réflexion quotidienne</p>
          </div>
        </div>
        <div className="text-white/60">
          <MessageCircle className="w-4 h-4 sm:w-5 sm:h-5" />
        </div>
      </div>

      {/* Question Content */}
      <div className="relative z-10 mb-4 sm:mb-6 flex-1">
        {loading ? (
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-white/80">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                <div className="w-2 h-2 bg-white/60 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
              </div>
              <span className="text-xs sm:text-sm">Préparation de votre question...</span>
            </div>
          </div>
        ) : (
          <div className="space-y-3 sm:space-y-4">
            <p className="text-white text-sm sm:text-base font-medium leading-relaxed line-clamp-3">
              {question}
            </p>
            <div className="flex items-center gap-2 text-purple-100">
              <span className="text-xs sm:text-sm">Touchez pour discuter avec l'IA</span>
              <ArrowRight className="w-3 h-3 sm:w-4 sm:h-4 group-hover:translate-x-1 group-active:translate-x-1 transition-transform" />
            </div>
          </div>
        )}
      </div>

      {/* Footer Badge */}
      <div className="relative z-10 mt-auto">
        <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm rounded-full px-2 sm:px-3 py-1">
          <div className="w-2 h-2 bg-green-400 rounded-full"></div>
          <span className="text-white text-xs font-medium">Nouveau</span>
        </div>
      </div>
    </div>
  );
};

export default ColorfulDailyQuestionCard;