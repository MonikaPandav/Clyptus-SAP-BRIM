import { useLayoutEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';

/** About is currently the /#about view; leave every other route/anchor alone. */
export function AboutScrollReset() {
  const { pathname, hash, key } = useLocation();
  const isAbout = pathname === '/' && hash === '#about';
  // A refreshed About history entry may already be marked manual by this component.
  const nativeRestoration = useRef<ScrollRestoration>(
    isAbout ? 'auto' : window.history.scrollRestoration,
  );

  useLayoutEffect(() => {
    if (!isAbout) return;

    window.history.scrollRestoration = 'manual';
    let firstFrame = 0;
    let secondFrame = 0;
    const reset = () => {
      if (window.location.pathname === '/' && window.location.hash === '#about') {
        window.scrollTo({ left: 0, top: 0, behavior: 'instant' });
      }
    };
    const resetAfterNavigation = () => {
      if (window.location.pathname !== '/' || window.location.hash !== '#about') return;
      window.history.scrollRestoration = 'manual';
      window.cancelAnimationFrame(firstFrame);
      window.cancelAnimationFrame(secondFrame);
      reset();
      // Native fragment/history scrolling can run after the navigation event.
      firstFrame = window.requestAnimationFrame(() => {
        reset();
        secondFrame = window.requestAnimationFrame(reset);
      });
    };
    const releaseRestoration = () => {
      window.cancelAnimationFrame(firstFrame);
      window.cancelAnimationFrame(secondFrame);
      window.history.scrollRestoration = nativeRestoration.current;
    };
    const handleRepeatLink = (event: MouseEvent) => {
      if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.altKey || event.shiftKey) return;
      const link = event.target instanceof Element ? event.target.closest('a') : null;
      if (!link || link.hasAttribute('download') || (link.target && link.target !== '_self')) return;
      // Re-selecting the same anchor does not necessarily emit hashchange/popstate.
      if (link.href === window.location.href) {
        event.preventDefault();
        resetAfterNavigation();
      }
    };

    window.addEventListener('pageshow', resetAfterNavigation);
    window.addEventListener('pagehide', releaseRestoration);
    window.addEventListener('popstate', resetAfterNavigation);
    window.addEventListener('hashchange', resetAfterNavigation);
    document.addEventListener('click', handleRepeatLink);
    resetAfterNavigation();

    return () => {
      window.cancelAnimationFrame(firstFrame);
      window.cancelAnimationFrame(secondFrame);
      window.removeEventListener('pageshow', resetAfterNavigation);
      window.removeEventListener('pagehide', releaseRestoration);
      window.removeEventListener('popstate', resetAfterNavigation);
      window.removeEventListener('hashchange', resetAfterNavigation);
      document.removeEventListener('click', handleRepeatLink);
      window.history.scrollRestoration = nativeRestoration.current;
    };
  }, [isAbout, pathname, hash, key]);

  return null;
}
