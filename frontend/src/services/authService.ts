import { apiClient } from './api'
import { User, LoginRequest, LoginResponse } from '@/types'

export const authService = {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    return apiClient.post<LoginResponse>('/auth/login', credentials)
  },

  async getCurrentUser(): Promise<User> {
    return apiClient.get<User>('/auth/me')
  },

  async register(userData: any): Promise<User> {
    return apiClient.post<User>('/auth/register', userData)
  },
}