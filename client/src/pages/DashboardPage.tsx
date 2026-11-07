
const recentlyPlayed = [
  { title: 'Weird Fishes/Arpeggi', artist: 'Radiohead', album: 'In Rainbows' },
  { title: 'My Love Mine All Mine', artist: 'Mitski', album: 'The Land Is Inhospitable and So Are We' },
  { title: '505', artist: 'Arctic Monkeys', album: 'Favourite Worst Nightmare' },
]

const topArtists = [
  { name: 'Radiohead', plays: 128 },
  { name: 'Mitski', plays: 96 },
  { name: 'Arctic Monkeys', plays: 84 },
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
        <div className="stat-card">
          <span>Total Tracks</span>
          <h2>248</h2>
        </div>

        <div className="stat-card">
          <span>Artists</span>
          <h2>42</h2>
        </div>

        <div className="stat-card">
          <span>Albums</span>
          <h2>86</h2>
        </div>

        <div className="stat-card">
          <span>Listening Time</span>
          <h2>126 hrs</h2>
        </div>
      </section>

      <section className="dashboard-section">
        <h2>Recently Played</h2>

        <div className="dashboard-list">
          {recentlyPlayed.map((track) => (
            <div className="dashboard-list-item" key={track.title}>
              <div>
                <strong>{track.title}</strong>
                <p>{track.artist} · {track.album}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="dashboard-section">
        <h2>Top Artists</h2>

        <div className="dashboard-list">
          {topArtists.map((artist) => (
            <div className="dashboard-list-item" key={artist.name}>
              <strong>{artist.name}</strong>
              <span>{artist.plays} plays</span>
            </div>
          ))}
        </div>
      </section>
    </>
  )
}

export default DashboardPage
