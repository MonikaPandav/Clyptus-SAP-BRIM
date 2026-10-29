import { lazy, Suspense, useEffect, useRef, useState } from 'react';

const LandingSections = lazy(() => import('./LandingSections'));
const sectionHashes = new Set(['#features', '#about', '#faq']);

export function DeferredLandingSections() {
  const marker = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(() => sectionHashes.has(window.location.hash));

  useEffect(() => {
    const revealHash = () => {
      if (sectionHashes.has(window.location.hash)) setReady(true);
    };
    window.addEventListener('hashchange', revealHash);
    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setReady(true);
        observer.disconnect();
      }
    }, { rootMargin: '400px' });
    if (marker.current) observer.observe(marker.current);
    return () => {
      observer.disconnect();
      window.removeEventListener('hashchange', revealHash);
    };
  }, []);

  return (
    <div ref={marker}>
      <Suspense fallback={<div className="landing-sections-placeholder" aria-busy="true" />}>
        {ready ? <LandingSections /> : <div className="landing-sections-placeholder" />}
      </Suspense>
    </div>
  );
}
