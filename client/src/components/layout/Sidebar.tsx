
const navigationItems = [
  { label: 'Overview', icon: '◫', href: '#dashboard' },
  { label: 'Artists', icon: '♫', href: '#artists' },
  { label: 'Albums', icon: '▤', href: '#albums' },
  { label: 'Tracks', icon: '♪', href: '#tracks' },
  { label: 'Listening History', icon: '◷', href: '#history' },
]

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="brand-icon">♫</span>
        <span>pakinggan</span>
      </div>

      <div className="sidebar-section">
        <p className="sidebar-heading">LIBRARY</p>

        <nav className="sidebar-nav">
          {navigationItems.map((item, index) => (
            <a
              key={item.label}
              href={item.href}
              className={`nav-item ${index === 0 ? 'active' : ''}`}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </a>
          ))}
        </nav>
      </div>

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
