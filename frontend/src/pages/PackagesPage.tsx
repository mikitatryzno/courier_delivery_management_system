import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useWebSocketContext } from '@/components/common/WebSocketProvider'
import { 
  Package, 
  Search, 
  Plus, 
  Filter, 
  Truck, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  Eye,
  Edit,
  Trash2
} from 'lucide-react'
import { Link } from 'react-router-dom'

interface Package {
  id: number
  title: string
  description?: string
  status: string
  sender_name: string
  sender_phone: string
  sender_address: string
  recipient_name: string
  recipient_phone: string
  recipient_address: string
  sender_id?: number
  courier_id?: number
  created_at: string
  updated_at: string
}

const statusColors = {
  created: 'bg-gray-100 text-gray-800',
  assigned: 'bg-blue-100 text-blue-800',
  picked_up: 'bg-yellow-100 text-yellow-800',
  in_transit: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800'
}

const statusIcons = {
  created: <Clock className="h-4 w-4" />,
  assigned: <Truck className="h-4 w-4" />,
  picked_up: <Package className="h-4 w-4" />,
  in_transit: <Truck className="h-4 w-4" />,
  delivered: <CheckCircle className="h-4 w-4" />,
  failed: <AlertCircle className="h-4 w-4" />
}

export default function PackagesPage() {
  const { user } = useAuth()
  const { lastMessage } = useWebSocketContext()
  const [packages, setPackages] = useState<Package[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [stats, setStats] = useState<any>(null)
  const packagesPerPage = 10

  useEffect(() => {
    fetchPackages()
    fetchStats()
  }, [currentPage, statusFilter, searchTerm])

  useEffect(() => {
    // Handle WebSocket package updates
    if (lastMessage && lastMessage.type === 'package_update') {
      fetchPackages() // Refresh packages on updates
    }
  }, [lastMessage])

  const fetchPackages = async () => {
    try {
      setLoading(true)
      const skip = (currentPage - 1) * packagesPerPage
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: packagesPerPage.toString()
      })

      if (statusFilter) params.append('status', statusFilter)
      if (searchTerm) params.append('search', searchTerm)

      const response = await fetch(`/api/packages/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setPackages(data)
      }
    } catch (error) {
      console.error('Error fetching packages:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/packages/stats', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error fetching stats:', error)
    }
  }

  const handleStatusUpdate = async (packageId: number, newStatus: string) => {
    try {
      const response = await fetch(`/api/packages/${packageId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ status: newStatus })
      })

      if (response.ok) {
        fetchPackages() // Refresh packages
      }
    } catch (error) {
      console.error('Error updating package status:', error)
    }
  }

  const handleAssignToSelf = async (packageId: number) => {
    try {
      const response = await fetch(`/api/packages/${packageId}/assign`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ courier_id: user?.id })
      })

      if (response.ok) {
        fetchPackages() // Refresh packages
      }
    } catch (error) {
      console.error('Error assigning package:', error)
    }
  }

  const canUpdateStatus = (pkg: Package) => {
    return (
      user?.role === 'admin' || 
      (user?.role === 'courier' && (pkg.courier_id === user.id || !pkg.courier_id))
    )
  }

  const canAssignToSelf = (pkg: Package) => {
    return user?.role === 'courier' && !pkg.courier_id && pkg.status === 'created'
  }

  const getNextStatus = (currentStatus: string) => {
    const statusFlow = {
      created: 'assigned',
      assigned: 'picked_up',
      picked_up: 'in_transit',
      in_transit: 'delivered'
    }
    return statusFlow[currentStatus as keyof typeof statusFlow]
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-semibold text-gray-900">Packages</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage and track package deliveries
          </p>
        </div>
        {(user?.role === 'sender' || user?.role === 'admin') && (
          <div className="mt-4 sm:mt-0">
            <Link
              to="/packages/create"
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              <Plus className="h-4 w-4 mr-2" />
              Create Package
            </Link>
          </div>
        )}
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Package className="h-6 w-6 text-gray-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Total Packages
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.total_packages}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <CheckCircle className="h-6 w-6 text-green-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Delivered
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.packages_by_status?.delivered || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Truck className="h-6 w-6 text-blue-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      In Transit
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.packages_by_status?.in_transit || 0}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white overflow-hidden shadow rounded-lg">
            <div className="p-5">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <Clock className="h-6 w-6 text-yellow-400" />
                </div>
                <div className="ml-5 w-0 flex-1">
                  <dl>
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Recent
                    </dt>
                    <dd className="text-lg font-medium text-gray-900">
                      {stats.recent_packages}
                    </dd>
                  </dl>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search packages..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <select
          className="px-3 py-2 border border-gray-300 rounded-md"
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
        >
          <option value="">All Statuses</option>
          <option value="created">Created</option>
          <option value="assigned">Assigned</option>
          <option value="picked_up">Picked Up</option>
          <option value="in_transit">In Transit</option>
          <option value="delivered">Delivered</option>
          <option value="failed">Failed</option>
        </select>
      </div>

      {/* Packages List */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Loading packages...</p>
          </div>
        ) : packages.length === 0 ? (
          <div className="text-center py-12">
            <Package className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No packages found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria or create a new package.
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {packages.map((pkg) => (
              <li key={pkg.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {statusIcons[pkg.status as keyof typeof statusIcons]}
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">
                        {pkg.title}
                      </p>
                      <p className="text-sm text-gray-500">
                        From: {pkg.sender_name} → To: {pkg.recipient_name}
                      </p>
                      <p className="text-xs text-gray-400">
                        Created: {new Date(pkg.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${statusColors[pkg.status as keyof typeof statusColors]}`}>
                      {pkg.status.replace('_', ' ')}
                    </span>
                    
                    <div className="flex items-center space-x-2">
                      <Link
                        to={`/packages/${pkg.id}`}
                        className="text-blue-600 hover:text-blue-900"
                      >
                        <Eye className="h-4 w-4" />
                      </Link>
                      
                      {canAssignToSelf(pkg) && (
                        <button
                          onClick={() => handleAssignToSelf(pkg.id)}
                          className="text-green-600 hover:text-green-900"
                          title="Assign to me"
                        >
                          <Truck className="h-4 w-4" />
                        </button>
                      )}
                      
                      {canUpdateStatus(pkg) && getNextStatus(pkg.status) && (
                        <button
                          onClick={() => handleStatusUpdate(pkg.id, getNextStatus(pkg.status)!)}
                          className="text-blue-600 hover:text-blue-900"
                          title={`Update to ${getNextStatus(pkg.status)}`}
                        >
                          <CheckCircle className="h-4 w-4" />
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}