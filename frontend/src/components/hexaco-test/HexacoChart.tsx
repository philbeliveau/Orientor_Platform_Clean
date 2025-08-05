'use client';

import React from 'react';
import { 
  Chart as ChartJS, 
  RadialLinearScale, 
  PointElement, 
  LineElement, 
  Filler, 
  Tooltip, 
  Legend 
} from 'chart.js';
import { Radar } from 'react-chartjs-2';
import { HexacoScoreResponse } from '@/services/hexacoTestService';

// Enregistrer les composants nécessaires pour le graphique radar
ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
);

// Définir les couleurs pour chaque domaine HEXACO
const hexacoColors: Record<string, string> = {
  'Honnêteté-Humilité': 'rgba(255, 99, 132, 0.7)',   // Rouge
  'Émotivité': 'rgba(54, 162, 235, 0.7)',             // Bleu
  'eXtraversion': 'rgba(255, 206, 86, 0.7)',          // Jaune
  'Agréabilité': 'rgba(75, 192, 192, 0.7)',           // Vert
  'Conscienciosité': 'rgba(153, 102, 255, 0.7)',      // Violet
  'Ouverture': 'rgba(255, 159, 64, 0.7)',             // Orange
};

// Mapping des clés de domaines vers les labels français
const domainLabels: Record<string, string> = {
  'honesty_humility': 'Honnêteté-Humilité',
  'emotionality': 'Émotivité',
  'extraversion': 'eXtraversion',
  'agreeableness': 'Agréabilité',
  'conscientiousness': 'Conscienciosité',
  'openness': 'Ouverture',
};

// Mapping des clés de domaines vers les labels anglais
const domainLabelsEn: Record<string, string> = {
  'honesty_humility': 'Honesty-Humility',
  'emotionality': 'Emotionality',
  'extraversion': 'eXtraversion',
  'agreeableness': 'Agreeableness',
  'conscientiousness': 'Conscientiousness',
  'openness': 'Openness',
};

interface HexacoChartProps {
  scores: HexacoScoreResponse;
  language?: string;
  showPercentiles?: boolean;
  size?: 'small' | 'medium' | 'large';
}

const HexacoChart: React.FC<HexacoChartProps> = ({ 
  scores, 
  language = 'fr', 
  showPercentiles = false,
  size = 'medium' 
}) => {
  // Choisir les labels selon la langue
  const labels = language === 'en' ? domainLabelsEn : domainLabels;
  
  // Préparer les données pour le graphique radar
  const orderedDomains = [
    'honesty_humility',
    'emotionality', 
    'extraversion',
    'agreeableness',
    'conscientiousness',
    'openness'
  ];

  // Utiliser les percentiles si demandé, sinon les scores bruts
  const dataToUse = showPercentiles ? scores.percentiles : scores.domains;
  
  const chartLabels = orderedDomains.map(domain => labels[domain] || domain);
  const chartData = orderedDomains.map(domain => dataToUse[domain] || 0);
  const chartColors = orderedDomains.map(domain => hexacoColors[labels[domain]] || 'rgba(128, 128, 128, 0.7)');

  const data = {
    labels: chartLabels,
    datasets: [
      {
        label: showPercentiles ? 'Percentiles HEXACO' : 'Scores HEXACO',
        data: chartData,
        backgroundColor: 'rgba(54, 162, 235, 0.2)',
        borderColor: 'rgba(54, 162, 235, 1)',
        borderWidth: 2,
        pointBackgroundColor: chartColors,
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(54, 162, 235, 1)',
        pointHoverRadius: 8,
      },
    ],
  };

  // Déterminer l'échelle maximale
  const maxScale = showPercentiles ? 100 : 5;

  // Options pour le graphique radar
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        min: 0,
        max: maxScale,
        ticks: {
          stepSize: showPercentiles ? 20 : 1,
          display: true,
          font: {
            size: size === 'small' ? 10 : size === 'large' ? 14 : 12,
          },
        },
        grid: {
          color: 'rgba(128, 128, 128, 0.2)',
        },
        angleLines: {
          color: 'rgba(128, 128, 128, 0.2)',
        },
        pointLabels: {
          font: {
            size: size === 'small' ? 11 : size === 'large' ? 16 : 13,
            weight: 'bold' as const,
          },
          color: 'rgba(75, 85, 99, 1)',
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            const label = context.dataset.label || '';
            const value = context.parsed.r;
            const suffix = showPercentiles ? 'e percentile' : '/5';
            return `${label}: ${value.toFixed(1)}${suffix}`;
          },
        },
      },
    },
    elements: {
      line: {
        tension: 0.1,
      },
    },
  };

  // Déterminer la hauteur selon la taille
  const height = size === 'small' ? 250 : size === 'large' ? 450 : 350;

  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      <Radar data={data} options={options} />
    </div>
  );
};

export default HexacoChart;