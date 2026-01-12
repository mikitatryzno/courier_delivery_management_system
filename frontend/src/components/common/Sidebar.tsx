import { NavLink } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { 
  LayoutDashboard, 
  Package, 
  Plus, 
  User,
  Truck,
  Users
} from 'lucide-react'
import { clsx } from 'clsx'

export default function Sidebar() {
  const { user } = useAuth()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, roles: ['admin', 'courier', 'sender', 'recipient'] },
    { name: 'Packages', href: '/packages', icon: Package, roles: ['admin', 'courier', 'sender', 'recipient'] },
    { name: 'Create Package', href: '/packages/create', icon: Plus, roles: ['admin', 'sender'] },
    { name: 'Profile', href: '/profile', icon: User, roles: ['admin', 'courier', 'sender', 'recipient'] },
  ]

  const filteredNavigation = navigation.filter(item => 
    item.roles.includes(user?.role || '')
  )

  return (
    <div className="w-64 bg-white shadow-sm h-screen">
      <nav className="mt-5 px-2">
        <div className="space-y-1">
          {filteredNavigation.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                clsx(
                  'group flex items-center px-2 py-2 text-sm font-medium rounded-md',
                  isActive
                    ? 'bg-blue-100 text-blue-900'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                )
              }
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.name}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}