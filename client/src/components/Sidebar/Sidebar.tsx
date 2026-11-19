import {
  Disc3,
  History,
  LayoutDashboard,
  LogOut,
  Music2,
  Users,
} from 'lucide-react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import './Sidebar.css'

// Defines the navigation sections displayed in the sidebar.
const navigationSections = [
  {
    heading: 'OVERVIEW',
    items: [{ label: 'Dashboard', icon: LayoutDashboard, path: '/' }],
  },
  {
    heading: 'LIBRARY',
    items: [
      { label: 'Artists', icon: Users, path: '/artists' },
      { label: 'Albums', icon: Disc3, path: '/albums' },
      { label: 'Tracks', icon: Music2, path: '/tracks' },
    ],
  },
  {
    heading: 'LISTENING',
    items: [{ label: 'Listening History', icon: History, path: '/history' }],
  },
]

// Displays application navigation, branding, and the authenticated user's profile.
function Sidebar() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  // Log out the user and return to the login page.
  function handleLogout() {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <aside className="sidebar">
      {/* Application branding */}
      <div className="sidebar-brand">
        <span className="brand-icon">
          <Music2 size={19} strokeWidth={2} />
        </span>
        <span className="brand-name">pakinggan</span>
      </div>

      {/* Navigation */}
      {navigationSections.map((section) => (
        <div className="sidebar-section" key={section.heading}>
          <p className="sidebar-heading">{section.heading}</p>

          <nav className="sidebar-nav" aria-label={section.heading}>
            {section.items.map((item) => {
              const Icon = item.icon

              return (
                <NavLink
                  key={item.label}
                  to={item.path}
                  end={item.path === '/'}
                  className={({ isActive }) =>
                    `nav-item ${isActive ? 'active' : ''}`
                  }
                >
                  <Icon
                    className="nav-icon"
                    size={18}
                    strokeWidth={1.8}
                    aria-hidden="true"
                  />
                  <span>{item.label}</span>
                </NavLink>
              )
            })}
          </nav>
        </div>
      ))}

      {/* User profile section */}
      <div className="sidebar-bottom">
        <div className="profile-avatar">
          {user?.username.charAt(0).toUpperCase()}
        </div>
        <div className="profile-info">
          <span>{user?.username}</span>
          <span className="profile-subtitle">Account</span>
        </div>
        <button
          className="profile-logout"
          type="button"
          onClick={handleLogout}
          aria-label="Log out"
          title="Log out"
        >
          <LogOut size={18} />
        </button>
      </div>
    </aside>
  )
}

export default Sidebar
