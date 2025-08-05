'use client';
import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

// Définition des thèmes de couleurs disponibles
export type ColorPalette = 'green' | 'blue' | 'gray' | 'yellowColors' | 'grayBlack';

export interface ColorTheme {
  id: ColorPalette;
  name: string;
  primaryColor: string;
  accentColor: string;
  borderColor: string;
  textColor: string;
  textColorLight: string;
  linkColor: string;
  linkHoverColor: string;
  variable: string;
}

// Définition des thèmes de couleurs disponibles
export const colorThemes: Record<ColorPalette, ColorTheme> = {
  green: {
    id: 'green',
    name: 'Vert Forêt',
    primaryColor: 'var(--color-cambridge_blue)',
    accentColor: 'var(--color-hookers_green)',
    borderColor: 'var(--color-dark_slate_gray)',
    textColor: 'var(--color-dark_slate_gray)',
    textColorLight: 'var(--color-cambridge_blue)',
    linkColor: 'var(--color-hookers_green)',
    linkHoverColor: 'var(--color-charcoal)',
    variable: '--color-green',
  },
  blue: {
    id: 'blue',
    name: 'Bleu Océan',
    primaryColor: 'var(--color-true_blue)',
    accentColor: 'var(--color-yale_blue)',
    borderColor: 'var(--color-oxford_blue_3)',
    textColor: 'var(--color-oxford_blue_1)',
    textColorLight: 'var(--color-true_blue)',
    linkColor: 'var(--color-yale_blue)',
    linkHoverColor: 'var(--color-oxford_blue_2)',
    variable: '--color-blue',
  },
  gray: {
    id: 'gray',
    name: 'Gris Neutre',
    primaryColor: 'var(--color-french_gray_1)',
    accentColor: 'var(--color-slate_gray)',
    borderColor: 'var(--color-onyx)',
    textColor: 'var(--color-eerie_black)',
    textColorLight: 'var(--color-french_gray_2)',
    linkColor: 'var(--color-slate_gray)',
    linkHoverColor: 'var(--color-outer_space)',
    variable: '--color-gray',
  },
  yellowColors: {
    id: 'yellowColors',
    name: 'yellow',
    primaryColor: 'var(--color-naples_yellow)',
    accentColor: 'var(--color-mustard)',
    borderColor: 'var(--color-golden_brown)',
    textColor: '#000',
    textColorLight: 'var(--color-field_drab_2)',
    linkColor: 'var(--color-saffron)',
    linkHoverColor: 'var(--color-dark_goldenrod_1)',
    variable: '--color-yellow',
  },
  grayBlack: {
    id: 'grayBlack',
    name: 'Gris-Noir',
    primaryColor: 'var(--color-gray)',
    accentColor: 'var(--color-black)',
    borderColor: 'var(--color-gray)',
    textColor: '#000',
    textColorLight: 'var(--color-gray)',
    linkColor: 'var(--color-gray)',
    linkHoverColor: 'var(--color-gray)',
    variable: '--color-gray-black',
  }
};

// Type pour le contexte de couleurs
type ColorContextType = {
  currentTheme: ColorTheme;
  setColorTheme: (themeId: ColorPalette) => void;
  availableThemes: ColorTheme[];
};

// Création du contexte avec des valeurs par défaut
const ColorContext = createContext<ColorContextType>({
  currentTheme: colorThemes.green,
  setColorTheme: () => {},
  availableThemes: Object.values(colorThemes),
});

// Hook personnalisé pour utiliser le contexte de couleurs
export const useColor = () => useContext(ColorContext);

// Provider pour le contexte de couleurs
export const ColorProvider = ({ children }: { children: ReactNode }) => {
  const [currentTheme, setCurrentTheme] = useState<ColorTheme>(colorThemes.green);

  useEffect(() => {
    // Récupérer le thème de couleurs stocké dans localStorage
    const storedTheme = localStorage.getItem('color-theme');
    if (storedTheme && colorThemes[storedTheme as ColorPalette]) {
      setCurrentTheme(colorThemes[storedTheme as ColorPalette]);
    }

    // Appliquer les classes CSS pour le thème de couleurs
    document.documentElement.style.setProperty('--primary-color', currentTheme.primaryColor);
    document.documentElement.style.setProperty('--accent-color', currentTheme.accentColor);
    document.documentElement.style.setProperty('--border-color', currentTheme.borderColor);
    document.documentElement.style.setProperty('--text-color', currentTheme.textColor);
    document.documentElement.style.setProperty('--text-color-light', currentTheme.textColorLight);
    document.documentElement.style.setProperty('--link-color', currentTheme.linkColor);
    document.documentElement.style.setProperty('--link-hover-color', currentTheme.linkHoverColor);
  }, [currentTheme]);

  // Fonction pour changer le thème de couleurs
  const setColorTheme = (themeId: ColorPalette) => {
    if (colorThemes[themeId]) {
      setCurrentTheme(colorThemes[themeId]);
      localStorage.setItem('color-theme', themeId);
    }
  };

  return (
    <ColorContext.Provider
      value={{
        currentTheme,
        setColorTheme,
        availableThemes: Object.values(colorThemes),
      }}
    >
      {children}
    </ColorContext.Provider>
  );
};