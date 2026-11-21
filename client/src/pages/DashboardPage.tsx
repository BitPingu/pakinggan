import { useLibrary } from '../hooks/useLibrary'
import PageHeader from '../components/PageHeader/PageHeader'
import EmptyState from '../components/EmptyState/EmptyState'
import { Clock, Disc3, Music, Music2, Users } from 'lucide-react'

// Displays the dashboard and library statistics.
function DashboardPage() {
  const { artists, albums, tracks, isLoading, error } = useLibrary()

  // Dashboard statistics displayed in the stat cards.
  const statistics = [
    {
      label: 'Total Tracks',
      value: isLoading ? '…' : error ? '—' : tracks.length.toString(),
      icon: Music,
    },
    {
      label: 'Artists',
      value: isLoading ? '…' : error ? '—' : artists.length.toString(),
      icon: Users,
    },
    {
      label: 'Albums',
      value: isLoading ? '…' : error ? '—' : albums.length.toString(),
      icon: Disc3,
    },
    { label: 'Listening Time', value: '—', icon: Clock },
  ]

  return (
    <>
      {/* Dashboard page heading */}
      <PageHeader
        eyebrow="YOUR MUSIC"
        title="Dashboard"
        description="Your listening activity, all in one place."
      />

      {/* Library statistics */}
      <section className="dashboard-stats">
        {statistics.map((stat) => (
          <div className="stat-card" key={stat.label}>
            <div className="stat-card-header">
              <span>{stat.label}</span>
              <stat.icon size={18} strokeWidth={1.8} aria-hidden="true" />
            </div>
            <h2>{stat.value}</h2>
          </div>
        ))}
      </section>

      {/* Dashboard loading error */}
      {error && <p className="form-error">{error}</p>}

      {/* Recently played tracks section */}
      <section className="dashboard-section">
        <h2>Recently Played</h2>
        <EmptyState
          icon={Music2}
          title="No listening history yet"
          description="Your recently played tracks will appear here once you start tracking your listening activity."
        />
      </section>

      {/* Top artists section */}
      <section className="dashboard-section">
        <h2>Top Artists</h2>
        <EmptyState
          icon={Users}
          title="No listening data yet"
          description="Your most listened-to artists will appear here once you start tracking your listening activity."
        />
      </section>
    </>
  )
}

export default DashboardPage
