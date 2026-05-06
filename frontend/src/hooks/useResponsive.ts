import { useState, useEffect } from 'react';

export type Breakpoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

const breakpointValues: Record<Breakpoint, number> = {
  xs: 0,
  sm: 576,
  md: 768,
  lg: 992,
  xl: 1200,
};

export function useResponsive() {
  const [breakpoint, setBreakpoint] = useState<Breakpoint>('xl');
  const [width, setWidth] = useState(window.innerWidth);

  useEffect(() => {
    const handleResize = () => {
      const w = window.innerWidth;
      setWidth(w);
      if (w < breakpointValues.sm) setBreakpoint('xs');
      else if (w < breakpointValues.md) setBreakpoint('sm');
      else if (w < breakpointValues.lg) setBreakpoint('md');
      else if (w < breakpointValues.xl) setBreakpoint('lg');
      else setBreakpoint('xl');
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    breakpoint,
    width,
    isMobile: width < breakpointValues.md,
    isTablet: width >= breakpointValues.md && width < breakpointValues.lg,
    isDesktop: width >= breakpointValues.lg,
    isTouchDevice: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
  };
}
