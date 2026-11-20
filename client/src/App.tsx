import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import LibraryProvider from './context/LibraryContext'
import AppLayout from './components/AppLayout/AppLayout'
import EmptyState from './components/EmptyState/EmptyState'
import { useAuth } from './hooks/useAuth'
import DashboardPage from './pages/DashboardPage'
import ArtistsPage from './pages/ArtistsPage'
import AlbumsPage from './pages/AlbumsPage'
import TracksPage from './pages/TracksPage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ForgotPasswordPage from './pages/ForgotPasswordPage'
import ResetPasswordPage from './pages/ResetPasswordPage'
import './App.css'

// Protects application pages from unauthenticated access.
function ProtectedLayout() {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <LibraryProvider>
      <AppLayout>
        <Outlet />
      </AppLayout>
    </LibraryProvider>
  )
}

// Defines the application's routes and page components.
function App() {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <EmptyState message="Loading..." />
  }

  return (
    <Routes>
      {/* Authentication pages */}
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <LoginPage />}
      />
      <Route
        path="/register"
        element={user ? <Navigate to="/" replace /> : <RegisterPage />}
      />
      <Route
        path="/forgot-password"
        element={user ? <Navigate to="/" replace /> : <ForgotPasswordPage />}
      />
      <Route
        path="/reset-password"
        element={user ? <Navigate to="/" replace /> : <ResetPasswordPage />}
      />

      {/* Protected application pages */}
      <Route element={<ProtectedLayout />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/artists" element={<ArtistsPage />} />
        <Route path="/albums" element={<AlbumsPage />} />
        <Route path="/tracks" element={<TracksPage />} />
      </Route>

      {/* Redirect unknown URLs */}
      <Route
        path="*"
        element={<Navigate to={user ? '/' : '/login'} replace />}
      />
    </Routes>
  )
}

export default App
