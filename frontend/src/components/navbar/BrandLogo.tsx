import React from 'react';
import { Link } from 'react-router-dom';
import fullLogoWhite from '../../assets/clyptusap-logo.png';
import fullLogoDark from '../../assets/clyptusap-logo-darktext.png';
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
  highlighted = false,
  className = '',
  imgClassName = '',
}) => {
  // Dimension presets for logo variants
  const sizeMap = {
    sm: { full: 'h-7', compact: 'h-7 w-7' },
    md: { full: 'h-8', compact: 'h-8 w-8' },
    lg: { full: 'h-10', compact: 'h-10 w-10' },
    xl: { full: 'h-12 md:h-14', compact: 'h-12 w-12' },
    '2xl': { full: 'h-14 md:h-16', compact: 'h-14 w-14' },
  };

  const selectedSize = sizeMap[size] || sizeMap.md;

  if (compact) {
    return (
      <Link
        className={`brand inline-flex items-center ${highlighted ? 'brand-highlighted' : ''
          } ${className}`}
        to="/"
        aria-label="Clyptusap.ai home"
      >
        <img
          className={`${selectedSize.compact} object-contain drop-shadow-sm ${highlighted ? 'brand-img-highlighted' : ''
            } ${imgClassName}`}
          src={iconOnly}
          alt="Clyptusap.ai"
        />
      </Link>
    );
  }

  return (
    <Link
      className={`brand inline-flex items-center gap-2.5 ${light ? 'brand-light' : ''} ${highlighted ? 'brand-highlighted' : ''
        } ${className}`}
      to="/"
      aria-label="Clyptusap.ai home"
    >
      {/* On dark surfaces show white text version; on light surfaces show dark text version */}
      <img
        className={`${selectedSize.full} w-auto object-contain dark:hidden ${highlighted ? 'brand-img-highlighted' : ''
          } ${imgClassName}`}
        src={fullLogoDark}
        alt="Clyptusap.ai"
      />
      <img
        className={`${selectedSize.full} w-auto object-contain hidden dark:block ${highlighted ? 'brand-img-highlighted' : ''
          } ${imgClassName}`}
        src={fullLogoWhite}
        alt="Clyptusap.ai"
      />
    </Link>
  );
};

