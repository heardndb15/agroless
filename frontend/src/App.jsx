import React, { useState } from 'react'
import Dashboard from './components/Dashboard'
import Auth from './components/Auth'

function App() {
  const [user, setUser] = useState(null)

  return (
    <div className="min-h-screen bg-green-50">
      {user ? (
        <Dashboard user={user} />
      ) : (
        <Auth onLogin={(userData) => setUser(userData)} />
      )}
    </div>
  )
}

export default App
