import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { studentAPI } from '../services/api';
import { User, Mail, Phone, MapPin, Calendar, Building } from 'lucide-react';
import { formatDate } from '../utils/helpers';

export default function Profile() {
  const { selectedStudent } = useAuth();
  const [loading, setLoading] = useState(true);
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    loadProfile();
  }, [selectedStudent]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      if (selectedStudent) {
        const response = await studentAPI.getProfile(selectedStudent);
        setProfile(response);
      }
    } catch (error) {
      console.error('Error loading profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const data = profile?.data;
  const photoUrl = data?.photo_url ? `http://localhost:8080${data.photo_url}` : null;

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="flex items-center gap-6">
          {photoUrl ? (
            <img
              src={photoUrl}
              alt={data?.name}
              className="w-24 h-24 rounded-full object-cover border-4 border-primary-100"
            />
          ) : (
            <div className="w-24 h-24 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white text-3xl font-bold">
              {data?.name?.charAt(0) || 'S'}
            </div>
          )}
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{data?.name}</h1>
            <p className="text-gray-600">{data?.code}</p>
            <p className="text-sm text-gray-500 mt-1">{data?.grade} - {data?.section}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Personal Information</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <User className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Full Name</p>
                <p className="font-medium">{data?.name || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Mail className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="font-medium">{data?.email || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Phone className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Phone</p>
                <p className="font-medium">{data?.phone || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <MapPin className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Address</p>
                <p className="font-medium">{data?.address || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Date of Birth</p>
                <p className="font-medium">{data?.date_of_birth ? formatDate(data.date_of_birth) : 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Academic Information</h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <Building className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Student Code</p>
                <p className="font-medium">{data?.code || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Building className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Grade</p>
                <p className="font-medium">{data?.grade || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Building className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Section</p>
                <p className="font-medium">{data?.section || 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Admission Date</p>
                <p className="font-medium">{data?.admission_date ? formatDate(data.admission_date) : 'N/A'}</p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Building className="w-5 h-5 text-gray-400 mt-0.5" />
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="font-medium capitalize">{data?.state || 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {data?.parent_ids && data.parent_ids.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Parent/Guardian Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {data.parent_ids.map((parent, index) => (
              <div key={index} className="border rounded-lg p-4">
                <h3 className="font-semibold text-lg mb-3">{parent.name}</h3>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Mail className="w-4 h-4 text-gray-400" />
                    <span className="text-sm">{parent.email || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Phone className="w-4 h-4 text-gray-400" />
                    <span className="text-sm">{parent.phone || 'N/A'}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4 text-gray-400" />
                    <span className="text-sm capitalize">{parent.relation || 'N/A'}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
