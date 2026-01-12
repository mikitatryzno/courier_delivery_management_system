import axios, { AxiosInstance, AxiosError } from 'axios'
import { ApiError } from '@/types'

class ApiClient {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
      return config
    })

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('access_token')
          window.location.href = '/login'
        }
        return Promise.reject(this.handleError(error))
      }
    )
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response?.data) {
      return error.response.data as ApiError
    }
    return {
      detail: error.message || 'An unexpected error occurred',
      status_code: error.response?.status || 500,
    }
  }

  async get<T>(url: string): Promise<T> {
    const response = await this.client.get<T>(url)
    return response.data
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data)
    return response.data
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<T>(url, data)
    return response.data
  }

  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<T>(url)
    return response.data
  }
}

export const apiClient = new ApiClient()