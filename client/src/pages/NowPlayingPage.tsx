import PageHeader from '../components/PageHeader/PageHeader'
import '../styles/now-playing.css'

// Displays the immersive Now Playing experience.
function NowPlayingPage() {
  return (
    <>
      {/* Now Playing page heading */}
      <PageHeader
        eyebrow="YOUR MUSIC"
        title="Now Playing"
        description="An immersive space for the music you're listening to."
      />

      {/* Main listening experience */}
      <section className="listening-experience">
        <div className="listening-track">
          <div className="listening-artwork-container">
            <img
              src="https://lastfm.freetls.fastly.net/i/u/500x500/example"
              alt="Album artwork"
              className="listening-artwork"
            />
          </div>

          <div className="listening-track-info">
            <span className="listening-status">
              <span className="now-playing-dot" />
              NOW PLAYING
            </span>

            <h2>Weird Fishes / Arpeggi</h2>
            <p className="listening-artist">Radiohead</p>
            <p className="listening-album">In Rainbows · 2007</p>

            <div className="listening-genres">
              <span>Alternative</span>
              <span>Art Rock</span>
              <span>Electronic</span>
            </div>
          </div>
        </div>
      </section>

      {/* Song information */}
      <section className="now-playing-section">
        <h2>About This Track</h2>
      </section>
    </>
  )
}

export default NowPlayingPage
