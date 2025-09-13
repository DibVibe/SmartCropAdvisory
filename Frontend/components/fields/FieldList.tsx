'use client'

import { useEffect, useState } from 'react'
import { useFieldStore } from '../../lib/store/fieldStore'
import Button from '@/components/ui/Button'
import FieldCard from './FieldCard'
import FieldForm from './FieldForm'

export default function FieldList() {
  const { fields, fetchFields, isLoading, selectField } = useFieldStore()
  const [showForm, setShowForm] = useState(false)

  useEffect(() => {
    fetchFields()
  }, [fetchFields])

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">My Fields</h1>
        <Button onClick={() => setShowForm(true)}>Add New Field</Button>
      </div>

      {fields.length === 0 ? (
        <div className="text-center py-12">
          <div className="mx-auto w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
            <span className="text-2xl">🌾</span>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No fields yet
          </h3>
          <p className="text-gray-600 mb-4">
            Get started by adding your first field
          </p>
          <Button onClick={() => setShowForm(true)}>Add Field</Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {fields.map((field) => (
            <FieldCard
              key={field.id}
              field={field}
              onClick={() => selectField(field)}
            />
          ))}
        </div>
      )}

      {showForm && (
        <FieldForm
          onClose={() => setShowForm(false)}
          onSuccess={() => setShowForm(false)}
        />
      )}
    </div>
  )
}
