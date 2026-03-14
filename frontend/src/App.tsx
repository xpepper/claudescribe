import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { TranscriptionList } from './pages/TranscriptionList'
import { TranscriptionDetail } from './pages/TranscriptionDetail'

export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<TranscriptionList />} />
        <Route path="/transcriptions/:id" element={<TranscriptionDetail />} />
      </Routes>
    </BrowserRouter>
  )
}
