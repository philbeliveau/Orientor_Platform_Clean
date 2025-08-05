export const extractChartData = (recommendation: any) => {
  if (!recommendation) return [];
  
  return [
    { 
      name: 'Analytical Thinking', 
      role: recommendation.analytical_thinking ?? 0,
      user: recommendation.user_analytical_thinking ?? 0
    },
    { 
      name: 'Attention to Detail', 
      role: recommendation.attention_to_detail ?? 0,
      user: recommendation.user_attention_to_detail ?? 0
    },
    { 
      name: 'Collaboration', 
      role: recommendation.collaboration ?? 0,
      user: recommendation.user_collaboration ?? 0
    },
    { 
      name: 'Adaptability', 
      role: recommendation.adaptability ?? 0,
      user: recommendation.user_adaptability ?? 0
    },
    { 
      name: 'Independence', 
      role: recommendation.independence ?? 0,
      user: recommendation.user_independence ?? 0
    },
    { 
      name: 'Evaluation', 
      role: recommendation.evaluation ?? 0,
      user: recommendation.user_evaluation ?? 0
    },
    { 
      name: 'Decision Making', 
      role: recommendation.decision_making ?? 0,
      user: recommendation.user_decision_making ?? 0
    },
    { 
      name: 'Stress Tolerance', 
      role: recommendation.stress_tolerance ?? 0,
      user: recommendation.user_stress_tolerance ?? 0
    }
  ];
}; 