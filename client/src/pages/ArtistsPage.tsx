function ArtistsPage() {
  return (
    <>
      <header className="page-header">
        <span className="page-eyebrow">YOUR LIBRARY</span>
        <h1>Artists</h1>
        <p className="page-description">
          Explore and manage the artists in your music library.
        </p>
      </header>

      <section className="artists-section">
        <div className="artists-section-header">
          <h2>Your Artists</h2>
          <span className="artists-count">0 artists</span>
        </div>

        <div className="dashboard-empty-state">
          <span className="empty-state-icon">♫</span>
          <h3>No artists yet</h3>
          <p>
            Artists you add to your library will appear here.
          </p>
        </div>
      </section>
    </>
  )
}

export default ArtistsPage
