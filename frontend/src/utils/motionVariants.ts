import { type Variants } from 'framer-motion';

/**
 * Standard cubic-bezier curves for premium, Apple/Linear-style fluid UI.
 */
export const transitions = {
  spring: {
    type: 'spring' as const,
    stiffness: 260,
    damping: 24,
  },
  smooth: {
    duration: 0.55,
    ease: [0.16, 1, 0.3, 1] as [number, number, number, number],
  },
  gentle: {
    duration: 0.7,
    ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
  },
  micro: {
    duration: 0.22,
    ease: [0.16, 1, 0.3, 1] as [number, number, number, number],
  },
};

/**
 * Default scroll viewport trigger configuration.
 * Triggers once naturally when the element is 12% into view, preventing flicker or repeating jumps.
 */
export const viewportOnce = {
  once: true,
  amount: 0.12,
  margin: '0px 0px -40px 0px',
};

export const viewportCard = {
  once: true,
  amount: 0.08,
  margin: '0px 0px -30px 0px',
};

/**
 * Standard Section Container Variants
 */
export const sectionContainerVariant: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.05,
    },
  },
};

/**
 * Section Header Fade-in & Slide-up Reveal
 */
export const sectionHeaderVariant: Variants = {
  hidden: { opacity: 0, y: 22 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
};

/**
 * Subtle Slide-up Reveal for Cards and Items
 */
export const fadeInUpVariant: Variants = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: transitions.smooth,
  },
};

/**
 * Stagger Container with customizable stagger delay
 */
export const staggerContainer = (staggerDelay = 0.08, delayChildren = 0.05): Variants => ({
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: staggerDelay,
      delayChildren,
    },
  },
});

/**
 * Feature Card Variant with Hover physics
 */
export const cardVariant: Variants = {
  hidden: { opacity: 0, y: 28, scale: 0.98 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: transitions.smooth,
  },
};

/**
 * Chip / Badge Variant
 */
export const chipVariant: Variants = {
  hidden: { opacity: 0, scale: 0.92 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transitions.micro,
  },
};

/**
 * Scale-in Variant for Visual Elements / Modals
 */
export const scaleInVariant: Variants = {
  hidden: { opacity: 0, scale: 0.94 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: transitions.gentle,
  },
};

/**
 * Cross-fade tab panel transition
 */
export const tabPanelVariant: Variants = {
  hidden: { opacity: 0, y: 12 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.35, ease: [0.16, 1, 0.3, 1] },
  },
  exit: {
    opacity: 0,
    y: -8,
    transition: { duration: 0.2, ease: 'easeOut' },
  },
};
