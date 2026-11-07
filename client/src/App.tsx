import { Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/layout/AppLayout'
import DashboardPage from './pages/DashboardPage'
import ArtistsPage from './pages/ArtistsPage'
import './App.css'

// Defines the application's routes and page components.
function App() {
  return (
    // Keeps the sidebar and main layout visible across all pages.
    <AppLayout>
      <Routes>
        {/* Dashboard page */}
        <Route path="/" element={<DashboardPage />} />

        {/* Artists library page */}
        <Route path="/artists" element={<ArtistsPage />} />

        {/* Redirect unknown URLs to the dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </AppLayout>
  )
}

export default App
