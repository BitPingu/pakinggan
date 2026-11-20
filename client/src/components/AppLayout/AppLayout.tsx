import { useState, type ReactNode } from 'react'
import Sidebar from '../Sidebar/Sidebar'
import './AppLayout.css'

interface AppLayoutProps {
  children: ReactNode
}

// Provides the shared layout used across all application pages.
function AppLayout({ children }: AppLayoutProps) {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(
    () => localStorage.getItem('sidebar-collapsed') === 'true',
  )

  // Toggles the sidebar and saves the user's preference.
  function toggleSidebar() {
    setIsSidebarCollapsed((current) => {
      const next = !current
      localStorage.setItem('sidebar-collapsed', String(next))
      return next
    })
  }

  return (
    <div
      className={`app-layout ${isSidebarCollapsed ? 'sidebar-collapsed' : ''}`}
    >
      <Sidebar isCollapsed={isSidebarCollapsed} onToggle={toggleSidebar} />

      <main className="main-content">{children}</main>
    </div>
  )
}

export default AppLayout
