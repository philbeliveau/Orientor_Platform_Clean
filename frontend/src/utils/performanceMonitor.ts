/**
 * Performance monitoring utilities for tracking web vitals and custom metrics
 */

interface PerformanceMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: Map<string, PerformanceMetric[]> = new Map();
  private observers: Map<string, PerformanceObserver> = new Map();

  constructor() {
    if (typeof window !== 'undefined') {
      this.initializeWebVitals();
    }
  }

  private initializeWebVitals() {
    // Largest Contentful Paint (LCP)
    this.observeMetric('largest-contentful-paint', (entries) => {
      const lastEntry = entries[entries.length - 1];
      this.recordMetric('LCP', lastEntry.startTime, this.rateLCP(lastEntry.startTime));
    });

    // First Input Delay (FID)
    this.observeMetric('first-input', (entries) => {
      const firstEntry = entries[0] as any;
      const fid = (firstEntry.processingStart || firstEntry.startTime) - firstEntry.startTime;
      this.recordMetric('FID', fid, this.rateFID(fid));
    });

    // Cumulative Layout Shift (CLS)
    let clsValue = 0;
    this.observeMetric('layout-shift', (entries) => {
      for (const entry of entries) {
        const layoutShiftEntry = entry as any;
        if (!layoutShiftEntry.hadRecentInput) {
          clsValue += layoutShiftEntry.value || 0;
        }
      }
      this.recordMetric('CLS', clsValue, this.rateCLS(clsValue));
    });

    // Time to First Byte (TTFB)
    if ('PerformanceNavigationTiming' in window) {
      const navTiming = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navTiming) {
        const ttfb = navTiming.responseStart - navTiming.fetchStart;
        this.recordMetric('TTFB', ttfb, this.rateTTFB(ttfb));
      }
    }

    // First Contentful Paint (FCP)
    this.observeMetric('paint', (entries) => {
      const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
      if (fcpEntry) {
        this.recordMetric('FCP', fcpEntry.startTime, this.rateFCP(fcpEntry.startTime));
      }
    });
  }

  private observeMetric(type: string, callback: (entries: PerformanceEntry[]) => void) {
    try {
      const observer = new PerformanceObserver((list) => {
        callback(list.getEntries());
      });
      observer.observe({ type, buffered: true });
      this.observers.set(type, observer);
    } catch (e) {
      console.warn(`Failed to observe ${type}:`, e);
    }
  }

  private recordMetric(name: string, value: number, rating: 'good' | 'needs-improvement' | 'poor') {
    const metric: PerformanceMetric = {
      name,
      value,
      rating,
      timestamp: Date.now()
    };

    const metrics = this.metrics.get(name) || [];
    metrics.push(metric);
    this.metrics.set(name, metrics);

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.log(`[Performance] ${name}: ${value.toFixed(2)}ms (${rating})`);
    }

    // Send to analytics if available
    this.sendToAnalytics(metric);
  }

  // Rating functions based on Web Vitals thresholds
  private rateLCP(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value <= 2500) return 'good';
    if (value <= 4000) return 'needs-improvement';
    return 'poor';
  }

  private rateFID(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value <= 100) return 'good';
    if (value <= 300) return 'needs-improvement';
    return 'poor';
  }

  private rateCLS(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value <= 0.1) return 'good';
    if (value <= 0.25) return 'needs-improvement';
    return 'poor';
  }

  private rateFCP(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value <= 1800) return 'good';
    if (value <= 3000) return 'needs-improvement';
    return 'poor';
  }

  private rateTTFB(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value <= 800) return 'good';
    if (value <= 1800) return 'needs-improvement';
    return 'poor';
  }

  private sendToAnalytics(metric: PerformanceMetric) {
    // Send to Vercel Analytics if available
    if (typeof window !== 'undefined' && (window as any).va) {
      (window as any).va('track', 'Web Vitals', {
        metric: metric.name,
        value: metric.value,
        rating: metric.rating
      });
    }
  }

  // Custom metric tracking
  measureTime(name: string): () => void {
    const start = performance.now();
    return () => {
      const duration = performance.now() - start;
      this.recordMetric(name, duration, this.rateCustomMetric(duration));
    };
  }

  private rateCustomMetric(value: number): 'good' | 'needs-improvement' | 'poor' {
    if (value <= 1000) return 'good';
    if (value <= 3000) return 'needs-improvement';
    return 'poor';
  }

  // Get current metrics
  getMetrics(): Record<string, PerformanceMetric[]> {
    return Object.fromEntries(this.metrics);
  }

  // Cleanup
  destroy() {
    this.observers.forEach(observer => observer.disconnect());
    this.observers.clear();
    this.metrics.clear();
  }
}

// Singleton instance
export const performanceMonitor = new PerformanceMonitor();

// React hook for performance monitoring
export function usePerformanceMonitor(componentName: string) {
  if (typeof window === 'undefined') return;

  const measureRender = performanceMonitor.measureTime(`${componentName}-render`);
  
  // Call this after component renders
  return {
    endMeasure: measureRender
  };
}

// Utility to measure async operations
export async function measureAsync<T>(
  name: string,
  operation: () => Promise<T>
): Promise<T> {
  const endMeasure = performanceMonitor.measureTime(name);
  try {
    const result = await operation();
    endMeasure();
    return result;
  } catch (error) {
    endMeasure();
    throw error;
  }
}