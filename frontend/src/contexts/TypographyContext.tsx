'use client';
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// Définition des thèmes de typographie disponibles
export type FontFamily = 'departure' | 'khand' | 'kola' | 'nippo' | 'technor';

export interface TypographyTheme {
  id: FontFamily;
  name: string;
  headingFont: string;
  bodyFont: string;
  monoFont: string;
  variable: string;
}

// Définition des thèmes de typographie disponibles
export const typographyThemes: Record<FontFamily, TypographyTheme> = {
  departure: {
    id: 'departure',
    name: 'Departure',
    headingFont: 'var(--font-departure)',
    bodyFont: 'var(--font-noto)',
    monoFont: 'var(--font-departure)',
    variable: '--font-departure',
  },
  khand: {
    id: 'khand',
    name: 'Khand',
    headingFont: 'var(--font-khand)',
    bodyFont: 'var(--font-noto)',
    monoFont: 'var(--font-departure)',
    variable: '--font-khand',
  },
  kola: {
    id: 'kola',
    name: 'Kola',
    headingFont: 'var(--font-kola)',
    bodyFont: 'var(--font-kola)',
    monoFont: 'var(--font-departure)',
    variable: '--font-kola',
  },
  nippo: {
    id: 'nippo',
    name: 'Nippo',
    headingFont: 'var(--font-nippo)',
    bodyFont: 'var(--font-nippo)',
    monoFont: 'var(--font-departure)',
    variable: '--font-nippo',
  },
  technor: {
    id: 'technor',
    name: 'Technor',
    headingFont: 'var(--font-technor)',
    bodyFont: 'var(--font-technor)',
    monoFont: 'var(--font-departure)',
    variable: '--font-technor',
  },
};

// Type pour le contexte de typographie
type TypographyContextType = {
  currentTheme: TypographyTheme;
  setTypographyTheme: (themeId: FontFamily) => void;
  availableThemes: TypographyTheme[];
};

// Création du contexte avec des valeurs par défaut
const TypographyContext = createContext<TypographyContextType>({
  currentTheme: typographyThemes.departure,
  setTypographyTheme: () => {},
  availableThemes: Object.values(typographyThemes),
});

// Hook personnalisé pour utiliser le contexte de typographie
export const useTypography = () => useContext(TypographyContext);

// Provider pour le contexte de typographie
export const TypographyProvider = ({ children }: { children: ReactNode }) => {
  const [currentTheme, setCurrentTheme] = useState<TypographyTheme>(typographyThemes.departure);

  useEffect(() => {
    // Récupérer le thème de typographie stocké dans localStorage
    const storedTheme = localStorage.getItem('typography-theme');
    if (storedTheme && typographyThemes[storedTheme as FontFamily]) {
      setCurrentTheme(typographyThemes[storedTheme as FontFamily]);
    }

    // Appliquer les classes CSS pour le thème de typographie
    document.documentElement.style.setProperty('--heading-font', currentTheme.headingFont);
    document.documentElement.style.setProperty('--body-font', currentTheme.bodyFont);
    document.documentElement.style.setProperty('--mono-font', currentTheme.monoFont);
  }, [currentTheme]);

  // Fonction pour changer le thème de typographie
  const setTypographyTheme = (themeId: FontFamily) => {
    if (typographyThemes[themeId]) {
      setCurrentTheme(typographyThemes[themeId]);
      localStorage.setItem('typography-theme', themeId);
    }
  };

  return (
    <TypographyContext.Provider
      value={{
        currentTheme,
        setTypographyTheme,
        availableThemes: Object.values(typographyThemes),
      }}
    >
      {children}
    </TypographyContext.Provider>
  );
};