import React, { useState, useEffect } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  ShieldCheck,
  Mail,
  Lock,
  User,
  Sparkles,
  AlertCircle,
  Eye,
  EyeOff,
  Info,
  X,
} from 'lucide-react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { PageMeta } from '../components/ui/PageMeta';
import { useAuth } from '../context/AuthContext';
import fullLogoDark from '../assets/clyptusap-logo-darktext.png';

export const LoginPage: React.FC = () => {
  const { user, login, register, guestLogin } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  const [mode, setMode] = useState<'login' | 'register'>(() => {
    return searchParams.get('mode') === 'register' ? 'register' : 'login';
  });

  useEffect(() => {
    const urlMode = searchParams.get('mode');
    if (urlMode === 'register' || urlMode === 'login') {
      setMode(urlMode);
    }
  }, [searchParams]);

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showForgotNotice, setShowForgotNotice] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // If already logged in with a real registered account, redirect to workspace
  useEffect(() => {
    if (user && !user.isGuest && user.email !== 'consultant@clyptusap.ai') {
      navigate('/app', { replace: true });
    }
  }, [user, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (mode === 'login') {
        await login(email.trim(), password);
      } else {
        if (!name.trim()) throw new Error('Please enter your full name');
        await register(name.trim(), email.trim(), password);
      }
      navigate('/app', { replace: true });
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials or try Demo Access.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoAccess = async () => {
    setLoading(true);
    try {
      await guestLogin();
      navigate('/app', { replace: true });
    } catch {
      navigate('/app', { replace: true });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <PageMeta
        title={mode === 'login' ? 'Sign In — Clyptus.AI' : 'Create Account — Clyptus.AI'}
        description="Continue to your Clyptus.AI enterprise SAP + BRIM knowledge workspace."
      />
      <main className="auth-layout-minimal">
        {/* Atmospheric Ambient Peach Gradient & Orbs */}
        <div className="auth-radial-glow" aria-hidden="true" />
        <div className="auth-ambient-orb orb-1" aria-hidden="true" />
        <div className="auth-ambient-orb orb-2" aria-hidden="true" />

        {/* Central Rounded Card Panel */}
        <section className="auth-card-panel">
          {/* Top Navigation Row */}
          <div className="auth-top-nav">
            <Link to="/" className="auth-back-link" title="Return to landing page">
              <ArrowLeft size={13} />
              <span>Back to home</span>
            </Link>
          </div>

          {/* Clean Clyptus Logo inside the sign-in box itself (no outer box, no inner bordered box, no background container, no shadow) */}
          <div className="auth-logo-center">
            <Link to="/" className="auth-logo-link" title="Return to Clyptus.AI Home">
              <img
                src={fullLogoDark}
                alt="Clyptus.AI"
                className="auth-logo-pure"
              />
            </Link>
          </div>

          {/* Header Copy */}
          <div className="auth-header-copy">
            <h1 className="auth-title">
              {mode === 'login' ? (
                <>Welcome to <span className="auth-brand-straight">Clyptus.AI</span></>
              ) : (
                <>Create Account on <span className="auth-brand-straight">Clyptus.AI</span></>
              )}
            </h1>
            <p className="auth-subtitle">
              Your intelligent SAP knowledge workspace
            </p>
          </div>

          {/* Clean Sign In / Create Account Tabs */}
          <div className="auth-tabs-pill" role="tablist">
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'login'}
              onClick={() => {
                setMode('login');
                setError(null);
                setShowForgotNotice(false);
              }}
              className={`auth-tab-btn ${mode === 'login' ? 'active' : ''}`}
            >
              Sign In
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'register'}
              onClick={() => {
                setMode('register');
                setError(null);
                setShowForgotNotice(false);
              }}
              className={`auth-tab-btn ${mode === 'register' ? 'active' : ''}`}
            >
              Create Account
            </button>
          </div>

          {/* Forgot Password Notice Modal */}
          {showForgotNotice && (
            <div className="auth-info-modal">
              <div className="info-modal-header">
                <div className="flex items-center gap-1.5">
                  <Info size={13} className="text-orange" />
                  <strong>Enterprise Password Recovery</strong>
                </div>
                <button
                  type="button"
                  onClick={() => setShowForgotNotice(false)}
                  className="info-modal-close"
                  aria-label="Close notification"
                >
                  <X size={14} />
                </button>
              </div>
              <p>
                In tenant-isolated enterprise environments, password resets require domain authorization.
                Please contact your SAP Lead or email <code>admin@clyptusap.ai</code> with your consultant ID to issue an encrypted reset link.
              </p>
            </div>
          )}

          {/* Error Message Banner */}
          {error && (
            <div className="auth-error-banner" role="alert">
              <AlertCircle size={15} className="shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Authentication Form */}
          <form onSubmit={handleSubmit} className="space-y-3.5">
            {mode === 'register' && (
              <div className="auth-input-group">
                <label className="auth-label" htmlFor="fullName">
                  Full Name
                </label>
                <div className="auth-input-wrapper">
                  <User size={15} className="auth-input-icon" />
                  <input
                    id="fullName"
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Elena Rostova"
                    className="auth-input-field"
                    autoComplete="name"
                  />
                </div>
              </div>
            )}

            <div className="auth-input-group">
              <label className="auth-label" htmlFor="emailAddress">
                Enterprise Email Address
              </label>
              <div className="auth-input-wrapper">
                <Mail size={15} className="auth-input-icon" />
                <input
                  id="emailAddress"
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="consultant@sap-enterprise.com"
                  className="auth-input-field"
                  autoComplete="email"
                />
              </div>
            </div>

            <div className="auth-input-group">
              <div className="auth-label-row">
                <label className="auth-label" htmlFor="accountPassword">
                  Password
                </label>
                {mode === 'login' && (
                  <button
                    type="button"
                    onClick={() => setShowForgotNotice(!showForgotNotice)}
                    className="auth-forgot-link"
                  >
                    Forgot password?
                  </button>
                )}
              </div>
              <div className="auth-input-wrapper">
                <Lock size={15} className="auth-input-icon" />
                <input
                  id="accountPassword"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="auth-input-field"
                  autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="auth-password-toggle"
                  title={showPassword ? 'Hide password' : 'Show password'}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            {/* Prominent Primary Button */}
            <button
              type="submit"
              disabled={loading}
              className="auth-submit-btn"
            >
              <span>
                {loading
                  ? 'Authenticating...'
                  : mode === 'login'
                    ? 'Sign In to Workspace'
                    : 'Create Workspace Account'}
              </span>
              <ArrowRight size={15} />
            </button>
          </form>

          {/* Quick Access Divider */}
          <div className="auth-divider-line">
            <span>or instant exploration</span>
          </div>

          {/* 1-Click Guest Test Drive */}
          <button
            type="button"
            onClick={handleDemoAccess}
            disabled={loading}
            className="auth-demo-btn"
            title="Explore Clyptus.AI instantly without registration"
          >
            <Sparkles size={14} className="text-orange" />
            <span>Instant Test Drive (1-Click Guest)</span>
            <ArrowRight size={13} />
          </button>

          {/* Enterprise Security Footer */}
          <div className="auth-security-footer">
            <ShieldCheck size={16} />
            <div>
              <span>Enterprise JWT Security &amp; Tenant Isolation</span>
              <br />
              <small className="text-stone-400">Connected to FastAPI &amp; PostgreSQL + pgvector RAG backend</small>
            </div>
          </div>

          {/* Legal / Informational Links */}
          <div className="auth-legal-footer">
            <span>Official SAP BRIM Implementation Guides</span>
            <span className="text-stone-300">·</span>
            <Link to="/how-it-works">How It Works</Link>
          </div>
        </section>
      </main>
    </>
  );
};
