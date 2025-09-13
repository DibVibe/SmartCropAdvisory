import { Field } from '../../lib1/types'
import { formatDate } from '../../lib1/utils'

interface FieldCardProps {
  field: Field
  onClick: () => void
}

export default function FieldCard({ field, onClick }: FieldCardProps) {
  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer border border-gray-200 p-6"
    >
      <div className="flex items-start justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">{field.name}</h3>
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
          Active
        </span>
      </div>

      <div className="space-y-2 text-sm text-gray-600">
        <div className="flex items-center">
          <span className="w-16">Area:</span>
          <span className="font-medium text-gray-900">{field.area} acres</span>
        </div>

        <div className="flex items-center">
          <span className="w-16">Crop:</span>
          <span className="font-medium text-gray-900 capitalize">
            {field.cropType}
          </span>
        </div>

        {field.soilType && (
          <div className="flex items-center">
            <span className="w-16">Soil:</span>
            <span className="font-medium text-gray-900 capitalize">
              {field.soilType}
            </span>
          </div>
        )}

        <div className="flex items-center">
          <span className="w-16">Added:</span>
          <span className="font-medium text-gray-900">
            {formatDate(field.createdAt)}
          </span>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">Location:</span>
          <span className="text-gray-900">
            {field.latitude.toFixed(4)}, {field.longitude.toFixed(4)}
          </span>
        </div>
      </div>
    </div>
  )
}
