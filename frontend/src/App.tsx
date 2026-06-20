import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DetailPage from './pages/DetailPage'
import AnalyzePage from './pages/AnalyzePage'
import ChartsPage from './pages/ChartsPage'
import ReportPage from './pages/ReportPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/detail/:id" element={<DetailPage />} />
        <Route path="/analyze/:id" element={<AnalyzePage />} />
        <Route path="/charts/:id" element={<ChartsPage />} />
        <Route path="/report/:id" element={<ReportPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
