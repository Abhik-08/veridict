import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { AuthProvider } from '@/context/AuthContext'
import { EvaluationProvider } from '@/context/EvaluationContext'
import './index.css'
import App from './App'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <EvaluationProvider>
        <App />
      </EvaluationProvider>
    </AuthProvider>
  </StrictMode>,
)
