import type { ReactNode } from 'react'
import Sidebar from '../Sidebar/Sidebar'
import './AppLayout.css'

interface AppLayoutProps {
  children: ReactNode
}

// Provides the shared layout used across all application pages.
function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="app-layout">
      {/* Persistent sidebar navigation */}
      <Sidebar />

      {/* Main content area for the active page */}
      <main className="main-content">{children}</main>
    </div>
  )
}

export default AppLayout
