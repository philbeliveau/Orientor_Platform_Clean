import React from 'react';

interface CourseCardProps {
  title: string;
  description: string;
  progress: number;
  color: string;
  icon: string;
  onClick?: () => void;
}

const CourseCard: React.FC<CourseCardProps> = ({
  title,
  description,
  progress,
  color,
  icon,
  onClick
}) => {
  // Determine background gradient based on color
  const getBackgroundClass = (color: string) => {
    switch (color) {
      case '#F59E0B':
        return 'bg-gradient-to-br from-yellow-500/90 to-yellow-600/90';
      case '#10B981':
        return 'bg-gradient-to-br from-green-500/90 to-green-600/90';
      case '#3B82F6':
        return 'bg-gradient-to-br from-blue-500/90 to-blue-600/90';
      case '#8B5CF6':
        return 'bg-gradient-to-br from-purple-500/90 to-purple-600/90';
      default:
        return 'bg-gradient-to-br from-gray-600/90 to-gray-700/90';
    }
  };

  const getHoverClass = (color: string) => {
    switch (color) {
      case '#F59E0B':
        return 'hover:from-yellow-400/95 hover:to-yellow-500/95';
      case '#10B981':
        return 'hover:from-green-400/95 hover:to-green-500/95';
      case '#3B82F6':
        return 'hover:from-blue-400/95 hover:to-blue-500/95';
      case '#8B5CF6':
        return 'hover:from-purple-400/95 hover:to-purple-500/95';
      default:
        return 'hover:from-gray-500/95 hover:to-gray-600/95';
    }
  };

  return (
    <div
      onClick={onClick}
      className={`
        relative overflow-hidden rounded-3xl p-6 sm:p-8 cursor-pointer 
        transform transition-all duration-300 ease-out hover:scale-105 hover:shadow-2xl
        border border-white/10 backdrop-blur-sm
        ${getBackgroundClass(color)} ${getHoverClass(color)}
        group
      `}
    >
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-4 right-4 w-32 h-32 rounded-full border border-white/20"></div>
        <div className="absolute bottom-8 left-8 w-24 h-24 rounded-full border border-white/10"></div>
        <div className="absolute top-1/2 left-1/4 w-16 h-16 rounded-full border border-white/10"></div>
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Icon */}
        <div className="mb-6">
          <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center backdrop-blur-sm border border-white/10">
            <span className="text-2xl">{icon}</span>
          </div>
        </div>

        {/* Title */}
        <h3 className="text-2xl sm:text-3xl font-light text-white mb-3 group-hover:text-white/95 transition-colors">
          {title}
        </h3>

        {/* Description */}
        <p className="text-white/80 text-base sm:text-lg mb-6 leading-relaxed">
          {description}
        </p>

        {/* Progress indicator and CTA */}
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-3">
              <div className="flex-1 bg-white/20 rounded-full h-2 overflow-hidden">
                <div 
                  className="h-full bg-white rounded-full transition-all duration-700 ease-out"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
              <span className="text-white/90 text-sm font-medium min-w-[3rem]">
                {progress}%
              </span>
            </div>
          </div>
          
          <div className="ml-6">
            <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/20 group-hover:bg-white/30 transition-all duration-200">
              <svg 
                className="w-5 h-5 text-white transform group-hover:translate-x-0.5 transition-transform duration-200" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path 
                  fillRule="evenodd" 
                  d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" 
                  clipRule="evenodd" 
                />
              </svg>
            </div>
          </div>
        </div>

        {/* Start Learning Button */}
        <div className="mt-6">
          <div className="flex items-center justify-between bg-black/20 rounded-2xl p-4 backdrop-blur-sm border border-white/10">
            <span className="text-white/90 font-medium text-lg">
              Start Learning
            </span>
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
              <svg 
                className="w-5 h-5 text-white" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path 
                  fillRule="evenodd" 
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" 
                  clipRule="evenodd" 
                />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Hover glow effect */}
      <div 
        className="absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-300 pointer-events-none rounded-3xl"
        style={{
          background: `radial-gradient(circle at 50% 50%, ${color}, transparent 70%)`
        }}
      ></div>
    </div>
  );
};

export default CourseCard;