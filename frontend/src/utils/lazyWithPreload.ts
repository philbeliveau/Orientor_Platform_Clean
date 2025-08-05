import { lazy, ComponentType, LazyExoticComponent } from 'react';

export interface PreloadableComponent<T extends ComponentType<any>>
  extends LazyExoticComponent<T> {
  preload: () => Promise<{ default: T }>;
}

/**
 * Creates a lazy-loaded component with preload capability
 * This allows us to start loading components before they're rendered
 */
export function lazyWithPreload<T extends ComponentType<any>>(
  factory: () => Promise<{ default: T }>
): PreloadableComponent<T> {
  const Component = lazy(factory) as PreloadableComponent<T>;
  Component.preload = factory;
  return Component;
}

/**
 * Preload multiple components at once
 */
export function preloadComponents(
  components: PreloadableComponent<any>[]
): Promise<any[]> {
  return Promise.all(components.map(component => component.preload()));
}

/**
 * Preload component on hover/focus
 */
export function usePreloadOnInteraction<T extends ComponentType<any>>(
  component: PreloadableComponent<T>
) {
  const preload = () => {
    component.preload();
  };

  return {
    onMouseEnter: preload,
    onFocus: preload,
    onTouchStart: preload,
  };
}