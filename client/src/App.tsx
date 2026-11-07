
import AppLayout from './components/layout/AppLayout'
import './App.css'

function App() {
  return (
    <AppLayout>
      <header className="page-header">
        <div>
          <p className="page-eyebrow">YOUR MUSIC</p>
          <h1>Overview</h1>
          <p className="page-description">
            Your listening activity, all in one place.
          </p>
        </div>
      </header>

      <section className="dashboard-placeholder">
        <h2>Welcome to Pakinggan</h2>
        <p>Your music journey starts here.</p>
      </section>
    </AppLayout>
  )
}

export default App
