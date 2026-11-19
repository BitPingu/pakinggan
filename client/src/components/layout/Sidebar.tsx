import { Disc3, History, LayoutDashboard, Music2, Users } from 'lucide-react'
import { NavLink } from 'react-router-dom'

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

function Sidebar() {
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
