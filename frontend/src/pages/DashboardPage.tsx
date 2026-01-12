import { useAuth } from '@/hooks/useAuth'
import { useQuery } from '@tanstack/react-query'
import { packageService } from '@/services/packageService'
import { Package2, Truck, CheckCircle, Clock } from 'lucide-react'

export default function DashboardPage() {
  const { user } = useAuth()
  
  const { data: packages = [], isLoading } = useQuery({
    queryKey: ['packages'],
    queryFn: packageService.getPackages,
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  const stats = {
    total: packages.length,
    inTransit: packages.filter(p => p.status === 'in_transit').length,
    delivered: packages.filter(p => p.status === 'delivered').length,
    pending: packages.filter(p => p.status === 'created').length,
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.name}!
        </h1>
        <p className="text-gray-600">Here's what's happening with your deliveries today.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Package2 className="h-8 w-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Packages</p>
              <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Truck className="h-8 w-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">In Transit</p>
              <p className="text-2xl font-bold text-gray-900">{stats.inTransit}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <CheckCircle className="h-8 w-8 text-green-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Delivered</p>
              <p className="text-2xl font-bold text-gray-900">{stats.delivered}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <Clock className="h-8 w-8 text-orange-600" />
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-bold text-gray-900">{stats.pending}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Packages</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {packages.slice(0, 5).map((pkg) => (
            <div key={pkg.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-900">{pkg.title}</p>
                  <p className="text-sm text-gray-500">
                    From: {pkg.senderName} → To: {pkg.recipientName}
                  </p>
                </div>
                <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                  pkg.status === 'delivered' ? 'bg-green-100 text-green-800' :
                  pkg.status === 'in_transit' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {pkg.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}