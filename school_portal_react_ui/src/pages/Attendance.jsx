import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { attendanceAPI } from '../services/api';
import { Calendar, CheckCircle, XCircle, Clock } from 'lucide-react';
import { formatDate, getAttendanceColor } from '../utils/helpers';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export default function Attendance() {
  const { selectedStudent } = useAuth();
  const [loading, setLoading] = useState(true);
  const [attendance, setAttendance] = useState(null);
  const [dateRange, setDateRange] = useState({
    from: '',
    to: '',
  });

  useEffect(() => {
    loadAttendance();
  }, [selectedStudent]);

  const loadAttendance = async () => {
    try {
      setLoading(true);
      if (selectedStudent) {
        const response = await attendanceAPI.getStudentAttendance(
          selectedStudent,
          dateRange.from || null,
          dateRange.to || null
        );
        setAttendance(response);
      }
    } catch (error) {
      console.error('Error loading attendance:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilter = () => {
    loadAttendance();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const summary = attendance?.data?.summary || {};
  const records = attendance?.data?.records || [];

  const pieData = [
    { name: 'Present', value: summary.present || 0, color: '#10b981' },
    { name: 'Absent', value: summary.absent || 0, color: '#ef4444' },
    { name: 'Late', value: summary.late || 0, color: '#f59e0b' },
  ];

  const monthlyData = records.reduce((acc, record) => {
    const month = new Date(record.date).toLocaleDateString('en-US', { month: 'short' });
    const existing = acc.find(item => item.month === month);
    if (existing) {
      existing[record.status] = (existing[record.status] || 0) + 1;
    } else {
      acc.push({ month, [record.status]: 1 });
    }
    return acc;
  }, []);

  return (
    <div className="space-y-6">
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Filter Attendance</h2>
        <div className="flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">From Date</label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange({ ...dateRange, from: e.target.value })}
              className="input"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">To Date</label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange({ ...dateRange, to: e.target.value })}
              className="input"
            />
          </div>
          <button onClick={handleFilter} className="btn-primary">
            Apply Filter
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Days</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{summary.total || 0}</p>
            </div>
            <div className="bg-blue-500 p-3 rounded-lg">
              <Calendar className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Present</p>
              <p className="text-2xl font-bold text-green-600 mt-1">{summary.present || 0}</p>
            </div>
            <div className="bg-green-500 p-3 rounded-lg">
              <CheckCircle className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Absent</p>
              <p className="text-2xl font-bold text-red-600 mt-1">{summary.absent || 0}</p>
            </div>
            <div className="bg-red-500 p-3 rounded-lg">
              <XCircle className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Attendance %</p>
              <p className="text-2xl font-bold text-purple-600 mt-1">{summary.attendance_percentage || 0}%</p>
            </div>
            <div className="bg-purple-500 p-3 rounded-lg">
              <Clock className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Attendance Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="card">
          <h2 className="text-lg font-semibold mb-4">Monthly Trend</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={monthlyData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="present" fill="#10b981" name="Present" />
              <Bar dataKey="absent" fill="#ef4444" name="Absent" />
              <Bar dataKey="late" fill="#f59e0b" name="Late" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Attendance Records</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Check In
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Check Out
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Remarks
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {records.map((record, index) => (
                <tr key={index} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(record.date)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getAttendanceColor(record.status)}`}>
                      {record.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.check_in || '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {record.check_out || '-'}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {record.remarks || '-'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
