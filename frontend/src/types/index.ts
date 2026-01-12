export interface User {
  id: string
  email: string
  name: string
  role: UserRole
  phone?: string
  createdAt: string
  updatedAt: string
}

export type UserRole = 'admin' | 'courier' | 'sender' | 'recipient'

export interface Package {
  id: string
  title: string
  description: string
  senderName: string
  senderPhone: string
  senderAddress: string
  recipientName: string
  recipientPhone: string
  recipientAddress: string
  status: PackageStatus
  courierId?: string
  courierName?: string
  createdAt: string
  updatedAt: string
  estimatedDelivery?: string
}

export type PackageStatus = 
  | 'created'
  | 'assigned'
  | 'picked_up'
  | 'in_transit'
  | 'delivered'
  | 'failed'
  | 'cancelled'

export interface CreatePackageRequest {
  title: string
  description: string
  senderName: string
  senderPhone: string
  senderAddress: string
  recipientName: string
  recipientPhone: string
  recipientAddress: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface ApiError {
  detail: string
  status_code: number
}