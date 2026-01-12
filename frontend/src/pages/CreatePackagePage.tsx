import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { packageService } from '@/services/packageService'
import { CreatePackageRequest } from '@/types'

const createPackageSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  description: z.string().min(1, 'Description is required'),
  senderName: z.string().min(1, 'Sender name is required'),
  senderPhone: z.string().min(1, 'Sender phone is required'),
  senderAddress: z.string().min(1, 'Sender address is required'),
  recipientName: z.string().min(1, 'Recipient name is required'),
  recipientPhone: z.string().min(1, 'Recipient phone is required'),
  recipientAddress: z.string().min(1, 'Recipient address is required'),
})

export default function CreatePackagePage() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [error, setError] = useState<string>('')

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreatePackageRequest>({
    resolver: zodResolver(createPackageSchema),
  })

  const createPackageMutation = useMutation({
    mutationFn: packageService.createPackage,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['packages'] })
      navigate('/packages')
    },
    onError: (err: any) => {
      setError(err.detail || 'Failed to create package')
    },
  })

  const onSubmit = (data: CreatePackageRequest) => {
    setError('')
    createPackageMutation.mutate(data)
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Create New Package</h1>
        <p className="text-gray-600">Fill in the details for your package delivery.</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium leading-6 text-gray-900">Package Information</h3>
              <p className="mt-1 text-sm text-gray-500">
                Basic details about the package.
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="grid grid-cols-6 gap-6">
                <div className="col-span-6">
                  <label className="block text-sm font-medium text-gray-700">
                    Package Title
                  </label>
                  <input
                    {...register('title')}
                    type="text"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.title && (
                    <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
                  )}
                </div>

                <div className="col-span-6">
                  <label className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    {...register('description')}
                    rows={3}
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.description && (
                    <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium leading-6 text-gray-900">Sender Information</h3>
              <p className="mt-1 text-sm text-gray-500">
                Details about the package sender.
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="grid grid-cols-6 gap-6">
                <div className="col-span-6 sm:col-span-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Sender Name
                  </label>
                  <input
                    {...register('senderName')}
                    type="text"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.senderName && (
                    <p className="mt-1 text-sm text-red-600">{errors.senderName.message}</p>
                  )}
                </div>

                <div className="col-span-6 sm:col-span-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Sender Phone
                  </label>
                  <input
                    {...register('senderPhone')}
                    type="tel"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.senderPhone && (
                    <p className="mt-1 text-sm text-red-600">{errors.senderPhone.message}</p>
                  )}
                </div>

                <div className="col-span-6">
                  <label className="block text-sm font-medium text-gray-700">
                    Sender Address
                  </label>
                  <input
                    {...register('senderAddress')}
                    type="text"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.senderAddress && (
                    <p className="mt-1 text-sm text-red-600">{errors.senderAddress.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white shadow px-4 py-5 sm:rounded-lg sm:p-6">
          <div className="md:grid md:grid-cols-3 md:gap-6">
            <div className="md:col-span-1">
              <h3 className="text-lg font-medium leading-6 text-gray-900">Recipient Information</h3>
              <p className="mt-1 text-sm text-gray-500">
                Details about the package recipient.
              </p>
            </div>
            <div className="mt-5 md:mt-0 md:col-span-2">
              <div className="grid grid-cols-6 gap-6">
                <div className="col-span-6 sm:col-span-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Recipient Name
                  </label>
                  <input
                    {...register('recipientName')}
                    type="text"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.recipientName && (
                    <p className="mt-1 text-sm text-red-600">{errors.recipientName.message}</p>
                  )}
                </div>

                <div className="col-span-6 sm:col-span-3">
                  <label className="block text-sm font-medium text-gray-700">
                    Recipient Phone
                  </label>
                  <input
                    {...register('recipientPhone')}
                    type="tel"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.recipientPhone && (
                    <p className="mt-1 text-sm text-red-600">{errors.recipientPhone.message}</p>
                  )}
                </div>

                <div className="col-span-6">
                  <label className="block text-sm font-medium text-gray-700">
                    Recipient Address
                  </label>
                  <input
                    {...register('recipientAddress')}
                    type="text"
                    className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  />
                  {errors.recipientAddress && (
                    <p className="mt-1 text-sm text-red-600">{errors.recipientAddress.message}</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={() => navigate('/packages')}
            className="bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={createPackageMutation.isPending}
            className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {createPackageMutation.isPending ? 'Creating...' : 'Create Package'}
          </button>
        </div>
      </form>
    </div>
  )
}