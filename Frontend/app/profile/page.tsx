'use client'

import { useState } from 'react'
import { 
  UserCircleIcon,
  PencilIcon,
  CameraIcon,
  MapPinIcon,
  PhoneIcon,
  EnvelopeIcon,
  CalendarIcon,
  GlobeAltIcon,
  BuildingOfficeIcon,
  ChartBarIcon,
  TrophyIcon,
  FireIcon,
  ClockIcon
} from '@heroicons/react/24/outline'

interface ProfileData {
  name: string
  email: string
  phone: string
  location: string
  company: string
  website: string
  bio: string
  joinDate: string
  farmType: string
  farmSize: string
  crops: string[]
  experience: string
}

export default function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false)
  const [profileData, setProfileData] = useState<ProfileData>({
    name: 'User Account',
    email: 'farmer@example.com',
    phone: '+1 (555) 123-4567',
    location: 'California, USA',
    company: 'Green Valley Farm',
    website: 'https://greenvalleyfarm.com',
    bio: 'Sustainable farming enthusiast with over 15 years of experience in precision agriculture. Passionate about leveraging technology to improve crop yields while maintaining environmental sustainability.',
    joinDate: '2024-01-15',
    farmType: 'Mixed Crops',
    farmSize: '250 acres',
    crops: ['Corn', 'Soybeans', 'Wheat', 'Tomatoes'],
    experience: '15+ years'
  })

  const [editData, setEditData] = useState<ProfileData>(profileData)

  const handleSave = () => {
    setProfileData(editData)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditData(profileData)
    setIsEditing(false)
  }

  const handleInputChange = (field: keyof ProfileData, value: any) => {
    setEditData(prev => ({ ...prev, [field]: value }))
  }

  const stats = [
    {
      label: 'Total Fields',
      value: '42',
      icon: MapPinIcon,
      color: 'text-green-600',
      bgColor: 'bg-green-100'
    },
    {
      label: 'Health Score',
      value: '94%',
      icon: ChartBarIcon,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100'
    },
    {
      label: 'Days Active',
      value: '245',
      icon: ClockIcon,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100'
    },
    {
      label: 'Alerts Resolved',
      value: '128',
      icon: TrophyIcon,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100'
    }
  ]

  const achievements = [
    {
      title: 'Early Adopter',
      description: 'One of the first 100 users to join SmartCropAdvisory',
      icon: FireIcon,
      earned: true,
      date: '2024-01-15'
    },
    {
      title: 'Data Driven',
      description: 'Used analytics features for 30 consecutive days',
      icon: ChartBarIcon,
      earned: true,
      date: '2024-02-14'
    },
    {
      title: 'Weather Watcher',
      description: 'Set up weather alerts for all fields',
      icon: GlobeAltIcon,
      earned: true,
      date: '2024-01-20'
    },
    {
      title: 'Disease Detective',
      description: 'Successfully identified and treated 10 crop diseases',
      icon: TrophyIcon,
      earned: false,
      date: null
    }
  ]

  return (
    <div className="max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary-100 rounded-xl flex items-center justify-center">
              <UserCircleIcon className="w-6 h-6 text-primary-600" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Profile</h1>
              <p className="text-gray-600">Manage your account information and preferences</p>
            </div>
          </div>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors duration-200"
          >
            <PencilIcon className="w-4 h-4" />
            <span>{isEditing ? 'Cancel' : 'Edit Profile'}</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Profile Card */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            {/* Profile Image */}
            <div className="text-center mb-6">
              <div className="relative inline-block">
                <div className="w-24 h-24 bg-primary-500 rounded-full flex items-center justify-center text-white text-3xl font-semibold">
                  {profileData.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                </div>
                {isEditing && (
                  <button className="absolute bottom-0 right-0 w-8 h-8 bg-gray-800 text-white rounded-full flex items-center justify-center hover:bg-gray-700 transition-colors">
                    <CameraIcon className="w-4 h-4" />
                  </button>
                )}
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mt-4">
                {profileData.name}
              </h2>
              <p className="text-gray-600">{profileData.company}</p>
            </div>

            {/* Contact Information */}
            <div className="space-y-4">
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <EnvelopeIcon className="w-4 h-4" />
                <span>{profileData.email}</span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <PhoneIcon className="w-4 h-4" />
                <span>{profileData.phone}</span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <MapPinIcon className="w-4 h-4" />
                <span>{profileData.location}</span>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <GlobeAltIcon className="w-4 h-4" />
                <a href={profileData.website} className="text-primary-600 hover:text-primary-700">
                  {profileData.website}
                </a>
              </div>
              <div className="flex items-center space-x-3 text-sm text-gray-600">
                <CalendarIcon className="w-4 h-4" />
                <span>Joined {new Date(profileData.joinDate).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Farm Info */}
            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">Farm Information</h3>
              <div className="space-y-2 text-sm text-gray-600">
                <div className="flex justify-between">
                  <span>Type:</span>
                  <span className="font-medium">{profileData.farmType}</span>
                </div>
                <div className="flex justify-between">
                  <span>Size:</span>
                  <span className="font-medium">{profileData.farmSize}</span>
                </div>
                <div className="flex justify-between">
                  <span>Experience:</span>
                  <span className="font-medium">{profileData.experience}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Stats Cards */}
          <div className="mt-8 grid grid-cols-2 gap-4">
            {stats.map((stat, index) => (
              <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
                <div className={`w-8 h-8 ${stat.bgColor} rounded-lg flex items-center justify-center mb-2`}>
                  <stat.icon className={`w-4 h-4 ${stat.color}`} />
                </div>
                <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
                <div className="text-xs text-gray-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-8">
          {/* Profile Information */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Profile Information</h3>
              {isEditing && (
                <div className="flex space-x-2">
                  <button
                    onClick={handleCancel}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSave}
                    className="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 transition-colors duration-200"
                  >
                    Save Changes
                  </button>
                </div>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Full Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.name}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Email Address
                </label>
                {isEditing ? (
                  <input
                    type="email"
                    value={editData.email}
                    onChange={(e) => handleInputChange('email', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.email}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Phone Number
                </label>
                {isEditing ? (
                  <input
                    type="tel"
                    value={editData.phone}
                    onChange={(e) => handleInputChange('phone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.phone}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Location
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.location}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Company/Farm Name
                </label>
                {isEditing ? (
                  <input
                    type="text"
                    value={editData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.company}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Website
                </label>
                {isEditing ? (
                  <input
                    type="url"
                    value={editData.website}
                    onChange={(e) => handleInputChange('website', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                ) : (
                  <a href={profileData.website} className="text-primary-600 hover:text-primary-700">
                    {profileData.website}
                  </a>
                )}
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Bio
                </label>
                {isEditing ? (
                  <textarea
                    value={editData.bio}
                    onChange={(e) => handleInputChange('bio', e.target.value)}
                    rows={4}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  />
                ) : (
                  <p className="text-gray-900">{profileData.bio}</p>
                )}
              </div>
            </div>
          </div>

          {/* Crops */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Crops Grown</h3>
            <div className="flex flex-wrap gap-2">
              {profileData.crops.map((crop, index) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                >
                  {crop}
                </span>
              ))}
              {isEditing && (
                <button className="px-3 py-1 border-2 border-dashed border-gray-300 text-gray-500 text-sm rounded-full hover:border-gray-400 transition-colors">
                  + Add Crop
                </button>
              )}
            </div>
          </div>

          {/* Achievements */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Achievements</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {achievements.map((achievement, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${
                    achievement.earned 
                      ? 'bg-primary-50 border-primary-200' 
                      : 'bg-gray-50 border-gray-200'
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      achievement.earned 
                        ? 'bg-primary-100 text-primary-600' 
                        : 'bg-gray-200 text-gray-400'
                    }`}>
                      <achievement.icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1">
                      <h4 className={`font-medium ${
                        achievement.earned ? 'text-gray-900' : 'text-gray-500'
                      }`}>
                        {achievement.title}
                      </h4>
                      <p className={`text-xs mt-1 ${
                        achievement.earned ? 'text-gray-600' : 'text-gray-400'
                      }`}>
                        {achievement.description}
                      </p>
                      {achievement.earned && achievement.date && (
                        <p className="text-xs text-primary-600 mt-1">
                          Earned {new Date(achievement.date).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
