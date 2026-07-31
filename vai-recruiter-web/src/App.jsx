import { useState } from 'react'
import './App.css'
import AuthScreen from './pages/AuthScreen'
import Workspace from './pages/Workspace'

function App() {
  const [session, setSession] = useState(() => JSON.parse(localStorage.getItem('talentscreen-session') || 'null'))

  if (!session) {
    return <AuthScreen onAuthenticated={setSession} />
  }

  return (
    <Workspace
      session={session}
      onLogout={() => { localStorage.removeItem('talentscreen-session'); setSession(null) }}
    />
  )
}

export default App
