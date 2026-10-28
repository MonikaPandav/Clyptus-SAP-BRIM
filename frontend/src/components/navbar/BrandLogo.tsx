import React from 'react';
import { Link } from 'react-router-dom';
import fullLogoDark from '../../assets/clyptusap-logo-darktext.png';
import fullLogoWhite from '../../assets/clyptusap-logo.png';
import iconOnly from '../../assets/clyptusap-icon.png';

interface BrandLogoProps {
  compact?: boolean;
  light?: boolean;
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl';
  highlighted?: boolean;
  className?: string;
  imgClassName?: string;
}

export const BrandLogo: React.FC<BrandLogoProps> = ({
  compact = false,
  light = false,
  size = 'md',
  className = '',
  imgClassName = '',
}) => {
  // Dimension presets for logo variants with slightly enlarged, crisp presence
  const sizeMap = {
    sm: { full: 'h-8', compact: 'h-8 w-8' },
    md: { full: 'h-10', compact: 'h-10 w-10' },
    lg: { full: 'h-12', compact: 'h-12 w-12' },
    xl: { full: 'h-13 md:h-15 lg:h-[58px]', compact: 'h-13 w-13' },
    '2xl': { full: 'h-15 md:h-17 lg:h-[64px]', compact: 'h-15 w-15' },
  };

  const selectedSize = sizeMap[size] || sizeMap.md;
  const activeLogo = light ? fullLogoWhite : fullLogoDark;

  if (compact) {
    return (
      <Link
        className={`brand inline-flex items-center ${className}`}
        to="/"
        aria-label="Clyptus.AI home"
      >
        <img
          className={`${selectedSize.compact} object-contain ${imgClassName}`}
          src={iconOnly}
          alt="Clyptus.AI"
        />
      </Link>
    );
  }

  return (
    <Link
      className={`brand inline-flex items-center ${className}`}
      to="/"
      aria-label="Clyptus.AI home"
    >
      {/* Single original full-color logo: absolutely no duplicate element in DOM */}
      <img
        className={`${selectedSize.full} w-auto object-contain ${imgClassName}`}
        src={activeLogo}
        alt="Clyptus.AI"
      />
    </Link>
  );
};
