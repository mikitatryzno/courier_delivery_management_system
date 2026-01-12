import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { User, LoginRequest, LoginResponse } from '@/types'
import { authService } from '@/services/authService'

interface AuthContextType {
  user: User | null
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
  isLoading: boolean
  isAuthenticated: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const userData = await authService.getCurrentUser()
          setUser(userData)
        } catch (error) {
          localStorage.removeItem('access_token')
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (credentials: LoginRequest) => {
    const response: LoginResponse = await authService.login(credentials)
    localStorage.setItem('access_token', response.access_token)
    setUser(response.user)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    setUser(null)
  }

  const value = {
    user,
    login,
    logout,
    isLoading,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}