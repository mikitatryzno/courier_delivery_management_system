import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { test, expect } from 'vitest'
import LoginPage from '@/pages/LoginPage'
import { AuthProvider } from '@/hooks/useAuth'

test('renders login page', () => {
  render(
    <AuthProvider>
      <LoginPage />
    </AuthProvider>
  )
  expect(screen.getByText(/Sign in to your account/i)).toBeInTheDocument()
})
