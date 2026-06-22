import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Evaluate from './pages/Evaluate'
import Decisions from './pages/Decisions'
import DecisionDetail from './pages/DecisionDetail'
import Provisioning from './pages/Provisioning'
import AuditLog from './pages/AuditLog'
import Policies from './pages/Policies'
import Companies from './pages/Companies'
import Assets from './pages/Assets'

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-slate-50">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/evaluate" element={<Evaluate />} />
            <Route path="/decisions" element={<Decisions />} />
            <Route path="/decisions/:id" element={<DecisionDetail />} />
            <Route path="/provisioning" element={<Provisioning />} />
            <Route path="/audit" element={<AuditLog />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/assets" element={<Assets />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
