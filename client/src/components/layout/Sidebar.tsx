import { NavLink } from 'react-router-dom'

// Defines the navigation items displayed in the sidebar.
const navigationItems = [
  { label: 'Overview', icon: '◫', path: '/' },
  { label: 'Artists', icon: '♫', path: '/artists' },
  { label: 'Albums', icon: '▤', path: '/albums' },
  { label: 'Tracks', icon: '♪', path: '/tracks' },
  { label: 'Listening History', icon: '◷', path: '/history' },
]

function Sidebar() {
  return (
    <aside className="sidebar">
      {/* Application branding */}
      <div className="sidebar-brand">
        <span className="brand-icon">♫</span>
        <span>pakinggan</span>
      </div>

      {/* Main navigation */}
      <div className="sidebar-section">
        <p className="sidebar-heading">LIBRARY</p>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <NavLink
              key={item.label}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                `nav-item ${isActive ? 'active' : ''}`
              }
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* User profile section */}
      <div className="sidebar-bottom">
        <div className="profile-avatar">U</div>
        <div className="profile-info">
          <span>Your Profile</span>
          <span className="profile-subtitle">Music enthusiast</span>
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
