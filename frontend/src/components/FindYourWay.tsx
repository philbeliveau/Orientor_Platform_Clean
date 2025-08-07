import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Card, CardContent, CircularProgress, Snackbar, Alert, useMediaQuery, useTheme, IconButton, Chip, Stack } from '@mui/material';
import { motion, useMotionValue, useTransform, PanInfo, animate } from 'framer-motion';
import RefreshIcon from '@mui/icons-material/Refresh';
import WorkIcon from '@mui/icons-material/Work';
import StarIcon from '@mui/icons-material/Star';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import { useClerkApi } from '@/services/api';
import SetCareerGoalButton from '@/components/common/SetCareerGoalButton';

interface CareerRecommendation {
  id: number;
  title: string;
  description: string;
  score: number;
  oasis_code?: string;
  main_duties?: string;
  metadata?: any;
}

const FindYourWay: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [careers, setCareers] = useState<CareerRecommendation[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success' as 'success' | 'error',
  });
  const api = useClerkApi();

  const x = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-10, 10]);
  const cardOpacity = useTransform(x, [-200, 0, 200], [0.5, 1, 0.5]);
  const dragConstraints = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchCareerRecommendations();
  }, []);

  const fetchCareerRecommendations = async () => {
    try {
      setLoading(true);
      const data = await api.getCareerRecommendations(); // Fetch recommendations
      setCareers(data as CareerRecommendation[]);
      setCurrentIndex(0);
      setError(null);
      console.log('Career recommendations:', data);
    } catch (err) {
      setError('Failed to load career recommendations. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDragEnd = async (event: MouseEvent | TouchEvent | PointerEvent, info: PanInfo) => {
    const swipeThreshold = 100;
    const career = careers[currentIndex];
    
    if (!career) return;

    if (info.offset.x > swipeThreshold) {
      await handleSwipeRight(career);
    } else if (info.offset.x < -swipeThreshold) {
      handleSwipeLeft();
    } else {
      // Reset position with spring animation
      animate(x, 0, {
        type: "spring",
        stiffness: 300,
        damping: 30,
        onComplete: () => {
          x.set(0);
        }
      });
    }
  };

  const handleSwipeRight = async (career: CareerRecommendation) => {
    try {
      await api.saveCareer({ id: career.id, title: career.title });
      setSnackbar({ open: true, message: `Saved "${career.title}" to your space!`, severity: 'success' });
      // Reset position with spring animation
      animate(x, 0, {
        type: "spring",
        stiffness: 300,
        damping: 30,
        onComplete: () => {
          x.set(0);
          setCurrentIndex(prev => prev + 1);
        }
      });
    } catch (err) {
      setSnackbar({ open: true, message: 'Failed to save career. Please try again.', severity: 'error' });
      console.error(err);
      // Reset position with spring animation
      animate(x, 0, {
        type: "spring",
        stiffness: 300,
        damping: 30,
        onComplete: () => {
          x.set(0);
        }
      });
    }
  };

  const handleSwipeLeft = () => {
    // Reset position with spring animation
    animate(x, 0, {
      type: "spring",
      stiffness: 300,
      damping: 30,
      onComplete: () => {
        x.set(0);
        setCurrentIndex(prev => prev + 1);
      }
    });
  };

  const currentCareer = careers[currentIndex];
  const hasMoreCareers = currentIndex < careers.length;
  
  // Extract skills from metadata if available
  const getSkills = (career: CareerRecommendation) => {
    if (!career.metadata) return [];
    
    const skills = [];
    // Extract skills from metadata - common fields that might contain skills
    const fields = ['skills', 'required_skills', 'competencies', 'technology_skills'];
    
    for (const field of fields) {
      if (career.metadata[field]) {
        const fieldSkills = career.metadata[field].split('|').map((s: string) => s.trim());
        skills.push(...fieldSkills);
      }
    }
    
    return skills.slice(0, 5); // Limit to 5 skills
  };

  return (
    <Box sx={{ 
      width: '100%', 
      p: 2, 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center',
      fontFamily: 'inter, monospace'
    }}>
      <Typography 
        variant="h4" 
        component="h1" 
        align="center" 
        sx={{ 
          mb: 6, 
          fontWeight: 'bold', 
          letterSpacing: 2,
          fontFamily: 'inter, monospace',
          background: 'black',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textShadow: '0px 2px 4px rgba(0,0,0,0.1)'
        }}
      >
        Discover Your Path
      </Typography>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 8 }}>
          <CircularProgress sx={{ color: '#2196F3' }} />
        </Box>
      ) : error ? (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography color="error" sx={{ fontFamily: 'inter, monospace' }}>{error}</Typography>
          <IconButton onClick={fetchCareerRecommendations} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>
      ) : !hasMoreCareers ? (
        <Box sx={{ textAlign: 'center', my: 4 }}>
          <Typography variant="h6" gutterBottom sx={{ fontFamily: 'inter, monospace' }}>
            No more career suggestions
          </Typography>
          <Typography paragraph color="textSecondary" sx={{ fontFamily: 'inter, monospace' }}>
            Check back later or refresh to see if we have new recommendations for you.
          </Typography>
          <IconButton onClick={fetchCareerRecommendations} color="primary">
            <RefreshIcon />
          </IconButton>
        </Box>
      ) : (
        <>
          <Box ref={dragConstraints} sx={{ 
            width: isMobile ? '100%' : '500px', 
            height: isMobile ? '400px' : '500px',
            position: 'relative',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            mb: 2,
            overflow: 'hidden'
          }}>
            <motion.div
              drag="x"
              dragConstraints={dragConstraints}
              dragElastic={0.7}
              onDragEnd={handleDragEnd}
              style={{
                x,
                rotate,
                opacity: cardOpacity,
                width: '100%',
                height: '100%',
                position: 'absolute',
                cursor: 'grab',
                transformOrigin: 'center center',
                touchAction: 'none'
              }}
              initial={{ x: 0, rotate: 0 }}
              animate={{ x: 0, rotate: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
            >
              <Card sx={{ 
                width: '100%', 
                height: '100%', 
                borderRadius: 4,
                boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
                background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)',
                border: '1px solid rgba(0,0,0,0.05)'
              }}>
                <CardContent sx={{ 
                  flex: 1, 
                  p: 3, 
                  display: 'flex', 
                  flexDirection: 'column',
                  height: '100%'
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <WorkIcon sx={{ color: '#59C2C9', mr: 1 }} />
                    <Typography 
                      variant="h5" 
                      component="h2" 
                      sx={{ 
                        fontWeight: 600, 
                        fontFamily: 'inter, monospace',
                        color: '#2A9D8F'
                      }}
                    >
                      {currentCareer.title}
                    </Typography>
                  </Box>

                  <Typography 
                    variant="body2" 
                    sx={{ 
                      flex: 1, 
                      overflow: 'auto', 
                      mb: 2, 
                      color: 'text.secondary', 
                      lineHeight: 1.6,
                      fontFamily: 'inter, monospace',
                      fontSize: '0.95rem'
                    }}
                  >
                    {currentCareer.description}
                  </Typography>
                  
                  {currentCareer.main_duties && (
                    <Box sx={{ mb: 2 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <TrendingUpIcon sx={{ color: '#59C2C9', mr: 1, fontSize: '1.2rem' }} />
                        <Typography 
                          variant="subtitle2" 
                          sx={{ 
                            fontWeight: 600,
                            fontFamily: 'inter, monospace',
                            color: '#2A9D8F'
                          }}
                        >
                          Main Duties:
                        </Typography>
                      </Box>
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: 'text.secondary',
                          fontFamily: 'inter, monospace',
                          pl: 3
                        }}
                      >
                        {currentCareer.main_duties}
                      </Typography>
                    </Box>
                  )}
                  
                  {currentCareer.metadata && (
                    <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1, mb: 2 }}>
                      {getSkills(currentCareer).map((skill, index) => (
                        <Chip 
                          key={index} 
                          label={skill} 
                          size="small" 
                          icon={<StarIcon sx={{ fontSize: '0.9rem', color: '#59C2C9' }} />}
                          sx={{ 
                            bgcolor: 'rgba(89,194,201,0.08)', 
                            color: '#2A9D8F',
                            fontFamily: 'inter, monospace',
                            '& .MuiChip-icon': {
                              color: '#59C2C9'
                            }
                          }} 
                        />
                      ))}
                    </Stack>
                  )}
                  
                  {/* Career Goal Button */}
                  <Box sx={{ mt: 'auto', mb: 2 }}>
                    <SetCareerGoalButton 
                      job={{
                        id: currentCareer.id.toString(),
                        oasis_code: currentCareer.oasis_code,
                        title: currentCareer.title,
                        description: currentCareer.description
                      }}
                      variant="primary"
                      size="md"
                      source="swipe"
                      className="w-full"
                    />
                  </Box>
                  
                  <Box sx={{ 
                    position: 'absolute', 
                    bottom: 24, 
                    left: 24, 
                    right: 24, 
                    display: 'flex', 
                    justifyContent: 'center', 
                    alignItems: 'center',
                    pointerEvents: 'none'
                  }}>
                    <Typography 
                      variant="caption" 
                      sx={{ 
                        fontWeight: 'bold', 
                        color: '#59C2C9', 
                        letterSpacing: 1.2, 
                        fontSize: '0.85rem',
                        textTransform: 'uppercase',
                        fontFamily: 'inter, monospace',
                        opacity: 0.8
                      }}
                    >
                      Swipe to Explore
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </motion.div>
          </Box>

          <Typography 
            variant="body2" 
            sx={{ 
              mt: 4, 
              textAlign: 'center', 
              color: 'text.secondary',
              fontFamily: 'inter, monospace',
              letterSpacing: 1
            }}
          >
            {currentIndex + 1} of {careers.length} recommendations
          </Typography>
        </>
      )}

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert 
          severity={snackbar.severity} 
          onClose={() => setSnackbar({ ...snackbar, open: false })} 
          sx={{ 
            fontFamily: 'inter, monospace',
            boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
          }}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default FindYourWay;