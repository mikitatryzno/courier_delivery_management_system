import { apiClient } from './api'
import { Package, CreatePackageRequest } from '@/types'

export const packageService = {
  async getPackages(): Promise<Package[]> {
    return apiClient.get<Package[]>('/packages')
  },

  async getPackage(id: string): Promise<Package> {
    return apiClient.get<Package>(`/packages/${id}`)
  },

  async createPackage(packageData: CreatePackageRequest): Promise<Package> {
    return apiClient.post<Package>('/packages', packageData)
  },

  async updatePackage(id: string, packageData: Partial<Package>): Promise<Package> {
    return apiClient.put<Package>(`/packages/${id}`, packageData)
  },

  async deletePackage(id: string): Promise<void> {
    return apiClient.delete<void>(`/packages/${id}`)
  },

  async updatePackageStatus(id: string, status: string): Promise<Package> {
    return apiClient.put<Package>(`/packages/${id}/status`, { status })
  },
}