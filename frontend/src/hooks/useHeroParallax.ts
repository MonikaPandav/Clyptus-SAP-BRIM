import { useEffect, useRef } from 'react';

/** Update compositor transforms without React renders or layout reads on scroll. */
export function useHeroParallax() {
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const hero = ref.current;
    if (!hero) return;
    const left = hero.querySelector<HTMLElement>('.orb-left');
    const right = hero.querySelector<HTMLElement>('.orb-right');
    const showcase = hero.querySelector<HTMLElement>('.hero-showcase-container');
    const glow = hero.querySelector<HTMLElement>('.hero-radial-glow');
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    let frame = 0;
    let top = 0;
    let height = 1;

    const update = () => {
      frame = 0;
      const progress = preference.matches ? 0 : Math.min(1, Math.max(0, (window.scrollY - top) / height));
      if (left) left.style.transform = `translateY(${progress * 80}px)`;
      if (right) right.style.transform = `translateY(${progress * -60}px)`;
      if (showcase) showcase.style.translate = `0 ${progress * 32}px`;
      if (glow) glow.style.transform = `scale(${1 + progress * 0.1})`;
    };
    const schedule = () => {
      if (!frame) frame = window.requestAnimationFrame(update);
    };
    const measure = () => {
      const rect = hero.getBoundingClientRect();
      top = rect.top + window.scrollY;
      height = rect.height || 1;
      schedule();
    };
    const observer = new ResizeObserver(measure);
    observer.observe(hero);
    window.addEventListener('scroll', schedule, { passive: true });
    window.addEventListener('resize', measure, { passive: true });
    preference.addEventListener('change', schedule);

    return () => {
      observer.disconnect();
      window.cancelAnimationFrame(frame);
      window.removeEventListener('scroll', schedule);
      window.removeEventListener('resize', measure);
      preference.removeEventListener('change', schedule);
    };
  }, []);

  return ref;
}
