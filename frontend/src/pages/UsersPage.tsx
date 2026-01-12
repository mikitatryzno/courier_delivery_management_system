import { useState, useEffect } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { Users, Search, Plus, Edit, Trash2, Shield, UserCheck } from 'lucide-react'

interface User {
  id: number
  email: string
  name: string
  role: string
  phone?: string
  created_at: string
  updated_at: string
}

export default function UsersPage() {
  const { user: currentUser } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedRole, setSelectedRole] = useState<string>('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalUsers, setTotalUsers] = useState(0)
  const usersPerPage = 10

  const roles = [
    { value: '', label: 'All Roles' },
    { value: 'admin', label: 'Admin' },
    { value: 'courier', label: 'Courier' },
    { value: 'sender', label: 'Sender' },
    { value: 'recipient', label: 'Recipient' }
  ]

  useEffect(() => {
    fetchUsers()
  }, [currentPage, selectedRole, searchTerm])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      const skip = (currentPage - 1) * usersPerPage
      const params = new URLSearchParams({
        skip: skip.toString(),
        limit: usersPerPage.toString()
      })

      if (selectedRole) params.append('role', selectedRole)
      if (searchTerm) params.append('search', searchTerm)

      const response = await fetch(`/api/users/?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        const data = await response.json()
        setUsers(data)
        // In a real implementation, you'd get total count from API
        setTotalUsers(data.length)
      }
    } catch (error) {
      console.error('Error fetching users:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleRoleChange = async (userId: number, newRole: string) => {
    try {
      const response = await fetch(`/api/users/${userId}/role`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({ role: newRole })
      })

      if (response.ok) {
        fetchUsers() // Refresh the list
      }
    } catch (error) {
      console.error('Error updating user role:', error)
    }
  }

  const handleDeleteUser = async (userId: number) => {
    if (!confirm('Are you sure you want to delete this user?')) return

    try {
      const response = await fetch(`/api/users/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      })

      if (response.ok) {
        fetchUsers() // Refresh the list
      }
    } catch (error) {
      console.error('Error deleting user:', error)
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin':
        return <Shield className="h-4 w-4 text-red-500" />
      case 'courier':
        return <UserCheck className="h-4 w-4 text-blue-500" />
      default:
        return <Users className="h-4 w-4 text-gray-500" />
    }
  }

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'bg-red-100 text-red-800'
      case 'courier':
        return 'bg-blue-100 text-blue-800'
      case 'sender':
        return 'bg-green-100 text-green-800'
      case 'recipient':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  if (currentUser?.role !== 'admin') {
    return (
      <div className="text-center py-12">
        <Shield className="mx-auto h-12 w-12 text-gray-400" />
        <h3 className="mt-2 text-sm font-medium text-gray-900">Access Denied</h3>
        <p className="mt-1 text-sm text-gray-500">
          You need admin privileges to access user management.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-xl font-semibold text-gray-900">User Management</h1>
          <p className="mt-2 text-sm text-gray-700">
            Manage system users and their roles.
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
            <input
              type="text"
              placeholder="Search users..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
        <select
          className="px-3 py-2 border border-gray-300 rounded-md"
          value={selectedRole}
          onChange={(e) => setSelectedRole(e.target.value)}
        >
          {roles.map((role) => (
            <option key={role.value} value={role.value}>
              {role.label}
            </option>
          ))}
        </select>
      </div>

      {/* Users Table */}
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-sm text-gray-500">Loading users...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-12">
            <Users className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No users found</h3>
            <p className="mt-1 text-sm text-gray-500">
              Try adjusting your search criteria.
            </p>
          </div>
        ) : (
          <ul className="divide-y divide-gray-200">
            {users.map((user) => (
              <li key={user.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {getRoleIcon(user.role)}
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">
                        {user.name}
                      </p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                      {user.phone && (
                        <p className="text-sm text-gray-500">{user.phone}</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRoleBadgeColor(user.role)}`}>
                      {user.role}
                    </span>
                    
                    <select
                      className="text-sm border border-gray-300 rounded px-2 py-1"
                      value={user.role}
                      onChange={(e) => handleRoleChange(user.id, e.target.value)}
                      disabled={user.id === currentUser?.id}
                    >
                      <option value="admin">Admin</option>
                      <option value="courier">Courier</option>
                      <option value="sender">Sender</option>
                      <option value="recipient">Recipient</option>
                    </select>
                    
                    <button
                      onClick={() => handleDeleteUser(user.id)}
                      disabled={user.id === currentUser?.id}
                      className="text-red-600 hover:text-red-900 disabled:text-gray-400 disabled:cursor-not-allowed"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Pagination would go here */}
    </div>
  )
}