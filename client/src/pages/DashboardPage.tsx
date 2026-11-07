
const statistics = [
  { label: 'Total Tracks', value: '0' },
  { label: 'Artists', value: '0' },
  { label: 'Albums', value: '0' },
  { label: 'Listening Time', value: '0 hrs' },
]

function DashboardPage() {
  return (
    <>
      <header className="page-header">
        <span className="page-eyebrow">YOUR MUSIC</span>
        <h1>Overview</h1>
        <p className="page-description">
          Your listening activity, all in one place.
        </p>
      </header>

      <section className="dashboard-stats">
        {statistics.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <span>{stat.label}</span>
            <h2>{stat.value}</h2>
          </div>
        ))}
      </section>

      <section className="dashboard-section">
        <h2>Recently Played</h2>

        <div className="dashboard-empty-state">
          <span className="empty-state-icon">♫</span>
          <h3>No listening history yet</h3>
          <p>
            Your recently played tracks will appear here once
            you start tracking your music.
          </p>
        </div>
      </section>

      <section className="dashboard-section">
        <h2>Top Artists</h2>

        <div className="dashboard-empty-state">
          <span className="empty-state-icon">♪</span>
          <h3>No artists yet</h3>
          <p>
            Your most listened-to artists will appear here.
          </p>
        </div>
      </section>
    </>
  )
}

export default DashboardPage
