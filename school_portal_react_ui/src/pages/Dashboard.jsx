import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { studentAPI, feeAPI, attendanceAPI } from '../services/api';
import { DollarSign, Calendar, TrendingUp, AlertCircle } from 'lucide-react';
import { formatCurrency, formatDate, getAttendanceColor } from '../utils/helpers';

export default function Dashboard() {
  const { selectedStudent } = useAuth();
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    profile: null,
    fees: null,
    attendance: null,
  });

  useEffect(() => {
    loadDashboardData();
  }, [selectedStudent]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      if (selectedStudent) {
        const profile = await studentAPI.getProfile(selectedStudent);
        const fees = await feeAPI.getStudentFees(selectedStudent);
        const attendance = await attendanceAPI.getStudentAttendance(selectedStudent);
        
        setData({ profile, fees, attendance });
      }
    } catch (error) {
      console.error('Error loading dashboard:', error);
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

  const stats = [
    {
      name: 'Total Fees',
      value: formatCurrency(data.fees?.data?.summary?.total || 0),
      icon: DollarSign,
      color: 'bg-blue-500',
    },
    {
      name: 'Fees Paid',
      value: formatCurrency(data.fees?.data?.summary?.paid || 0),
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      name: 'Fees Due',
      value: formatCurrency(data.fees?.data?.summary?.due || 0),
      icon: AlertCircle,
      color: 'bg-red-500',
    },
    {
      name: 'Attendance',
      value: `${data.attendance?.data?.summary?.attendance_percentage || 0}%`,
      icon: Calendar,
      color: 'bg-purple-500',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        {data.profile?.data?.photo_url ? (
          <img
            src={`http://localhost:8080${data.profile.data.photo_url}`}
            alt={data.profile.data.name}
            className="w-16 h-16 rounded-full object-cover border-2 border-primary-200"
          />
        ) : (
          <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
            {data.profile?.data?.name?.charAt(0) || 'S'}
          </div>
        )}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Welcome back!</h1>
          <p className="text-gray-600 mt-1">Here's your overview</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">{stat.name}</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                </div>
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {data.profile?.data && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Student Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Name</p>
              <p className="font-medium">{data.profile.data.name}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Student Code</p>
              <p className="font-medium">{data.profile.data.code}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Grade</p>
              <p className="font-medium">{data.profile.data.grade || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Section</p>
              <p className="font-medium">{data.profile.data.section || 'N/A'}</p>
            </div>
          </div>
        </div>
      )}

      {data.fees?.data?.fees && data.fees.data.fees.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Recent Fees</h2>
          <div className="space-y-3">
            {data.fees.data.fees.slice(0, 3).map((fee) => (
              <div key={fee.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <p className="font-medium">{fee.display_name}</p>
                  <p className="text-sm text-gray-600">{fee.academic_year} - {fee.term}</p>
                </div>
                <div className="text-right">
                  <p className="font-semibold">{formatCurrency(fee.amount_total)}</p>
                  <p className={`text-sm ${fee.payment_state === 'paid' ? 'text-green-600' : 'text-red-600'}`}>
                    {fee.payment_state === 'paid' ? 'Paid' : `Due: ${formatCurrency(fee.amount_due)}`}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
