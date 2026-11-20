import { Navigate, Outlet, Route, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout/AppLayout'
import EmptyState from './components/EmptyState/EmptyState'
import { useAuth } from './hooks/useAuth'
import DashboardPage from './pages/DashboardPage'
import ArtistsPage from './pages/ArtistsPage'
import AlbumsPage from './pages/AlbumsPage'
import TracksPage from './pages/TracksPage'
import LoginPage from './pages/LoginPage'
import './App.css'

// Protects application pages from unauthenticated access.
function ProtectedLayout() {
  const { user } = useAuth()

  if (!user) {
    return <Navigate to="/login" replace />
  }

  return (
    <AppLayout>
      <Outlet />
    </AppLayout>
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
      {/* Authentication page */}
      <Route
        path="/login"
        element={user ? <Navigate to="/" replace /> : <LoginPage />}
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
