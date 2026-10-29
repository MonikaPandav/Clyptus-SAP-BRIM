import { lazy, Suspense } from 'react';
import { BrowserRouter, Navigate, Outlet, Route, Routes } from 'react-router-dom';
import { LandingPage } from './pages/LandingPage';
import { AboutScrollReset } from './components/navigation/AboutScrollReset';

const FeaturesPage = lazy(() => import('./pages/FeaturesPage').then(m => ({ default: m.FeaturesPage })));
const HowItWorksPage = lazy(() => import('./pages/HowItWorksPage').then(m => ({ default: m.HowItWorksPage })));
const LoginPage = lazy(() => import('./pages/LoginPage').then(m => ({ default: m.LoginPage })));
const AdminLoginPage = lazy(() => import('./pages/admin/AdminLoginPage').then(m => ({ default: m.AdminLoginPage })));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard').then(m => ({ default: m.AdminDashboard })));
const OnboardingPage = lazy(() => import('./pages/OnboardingPage').then(m => ({ default: m.OnboardingPage })));
const ChatPage = lazy(() => import('./pages/ChatPage').then(m => ({ default: m.ChatPage })));
const ProjectPage = lazy(() => import('./pages/ProjectPage').then(m => ({ default: m.ProjectPage })));
const SettingsPage = lazy(() => import('./pages/SettingsPage').then(m => ({ default: m.SettingsPage })));
const ProfilePage = lazy(() => import('./pages/ProfilePage').then(m => ({ default: m.ProfilePage })));
const SharedPromptPage = lazy(() => import('./pages/SharedPromptPage').then(m => ({ default: m.SharedPromptPage })));
const AppLayout = lazy(() => import('./layouts/AppLayout').then(m => ({ default: m.AppLayout })));
const ProtectedRoute = lazy(() => import('./layouts/ProtectedRoute').then(m => ({ default: m.ProtectedRoute })));
const AdminProtectedRoute = lazy(() => import('./layouts/AdminProtectedRoute').then(m => ({ default: m.AdminProtectedRoute })));
const AuthProvider = lazy(() => import('./context/AuthContext').then(m => ({ default: m.AuthProvider })));

function SessionRoutes() {
  return <AuthProvider><Outlet /></AuthProvider>;
}

export default function App() {
  return (
    <BrowserRouter>
      <AboutScrollReset />
      <Suspense fallback={<div className="route-loading" role="status">Loading Clyptus.AI...</div>}>
        <Routes>
          {/* Public Landing & Marketing */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/how-it-works" element={<HowItWorksPage />} />
          <Route path="/share/:token" element={<SharedPromptPage />} />

          <Route element={<SessionRoutes />}>
            <Route path="/login" element={<LoginPage />} />

            {/* Dedicated Super Admin Authentication Gateway */}
            <Route path="/admin/login" element={<AdminLoginPage />} />
            <Route path="/admin-login" element={<Navigate to="/admin/login" replace />} />

            {/* Dedicated Super Admin Dashboard (Strictly Admin Protected) */}
            <Route
              path="/admin"
              element={
                <AdminProtectedRoute>
                  <AdminDashboard />
                </AdminProtectedRoute>
              }
            />

            {/* Onboarding */}
            <Route
              path="/onboarding"
              element={
                <ProtectedRoute>
                  <OnboardingPage />
                </ProtectedRoute>
              }
            />

            {/* Authenticated Workspace */}
            <Route
              path="/app"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<ChatPage />} />
              <Route path="chat/:conversationId" element={<ChatPage />} />
              {/* Direct documents route is strictly blocked for non-admin and redirects to admin dashboard */}
              <Route
                path="documents"
                element={
                  <AdminProtectedRoute>
                    <Navigate to="/admin" replace />
                  </AdminProtectedRoute>
                }
              />
              <Route path="projects/:projectId" element={<ProjectPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="profile" element={<ProfilePage />} />
              <Route path="*" element={<Navigate to="/app" replace />} />
            </Route>

          </Route>

          {/* Catch-all redirect to Landing */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
