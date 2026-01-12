import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './hooks/useAuth'
import { WebSocketProvider } from './components/common/WebSocketProvider'
import Layout from './components/common/Layout'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'
import PackagesPage from './pages/PackagesPage'
import CreatePackagePage from './pages/CreatePackagePage'
import ProfilePage from './pages/ProfilePage'
import LiveTrackingPage from './pages/LiveTrackingPage'
import ProtectedRoute from './components/common/ProtectedRoute'
import './App.css'

function App() {
  return (
    <AuthProvider>
      <WebSocketProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="packages" element={<PackagesPage />} />
              <Route path="packages/create" element={<CreatePackagePage />} />
              <Route path="track/:deliveryId" element={<LiveTrackingPage />} />
              <Route path="profile" element={<ProfilePage />} />
            </Route>
          </Routes>
        </Router>
      </WebSocketProvider>
    </AuthProvider>
  )
}

export default App