import React, { useState } from 'react';
import { ArrowUpRight, LogIn, Menu, X } from 'lucide-react';
import { Link, NavLink } from 'react-router-dom';
import { BrandLogo } from './BrandLogo';

export const PublicNav: React.FC = () => {
  const [open, setOpen] = useState(false);

  return (
    <header className="public-nav">
      <div className="nav-inner">
        <BrandLogo size="xl" highlighted />
        <button
          className="icon-button mobile-menu-toggle"
          aria-label={open ? 'Close navigation' : 'Open navigation'}
          onClick={() => setOpen(!open)}
        >
          {open ? <X size={19} /> : <Menu size={19} />}
        </button>
        <nav className={`nav-links ${open ? 'nav-links-open' : ''}`} aria-label="Main navigation">
          <NavLink to="/features" onClick={() => setOpen(false)}>Features</NavLink>
          <NavLink to="/how-it-works" onClick={() => setOpen(false)}>How it works</NavLink>
          <a href="/#about" onClick={() => setOpen(false)}>About</a>
          <a href="/#faq" onClick={() => setOpen(false)}>FAQs</a>
          <div className="mobile-nav-actions">
            <Link className="nav-signin" to="/login" onClick={() => setOpen(false)}>
              <LogIn size={14} />
              <span>Sign in</span>
            </Link>
            <Link className="button button-brand button-small" to="/login" onClick={() => setOpen(false)}>
              Try now <ArrowUpRight size={15} />
            </Link>
          </div>
        </nav>
        <div className="nav-actions">
          <Link className="nav-signin" to="/login">
            <LogIn size={14} />
            <span>Sign in</span>
          </Link>
          <Link className="button button-brand button-small" to="/login">
            Try now <ArrowUpRight size={15} />
          </Link>
        </div>
      </div>
    </header>
  );
};
