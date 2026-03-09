import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { gradesAPI } from '../services/api';
import { BookOpen, Award, TrendingUp, FileText } from 'lucide-react';

export default function Grades() {
  const { selectedStudent } = useAuth();
  const [loading, setLoading] = useState(true);
  const [grades, setGrades] = useState(null);
  const [selectedReport, setSelectedReport] = useState(null);

  useEffect(() => {
    loadGrades();
  }, [selectedStudent]);

  const loadGrades = async () => {
    try {
      setLoading(true);
      if (selectedStudent) {
        console.log('Loading grades for student:', selectedStudent);
        const response = await gradesAPI.getStudentGrades(selectedStudent);
        console.log('Grades response:', response);
        setGrades(response);
        if (response?.data?.report_cards?.length > 0) {
          setSelectedReport(response.data.report_cards[0]);
        }
      }
    } catch (error) {
      console.error('Error loading grades:', error);
      console.error('Error response:', error.response?.data);
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

  const reportCards = grades?.data?.report_cards || [];

  if (reportCards.length === 0) {
    return (
      <div className="card text-center py-12">
        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-900 mb-2">No Report Cards Available</h3>
        <p className="text-gray-600">Report cards will appear here once published by the school.</p>
      </div>
    );
  }

  const getGradeColor = (percentage) => {
    if (percentage >= 90) return 'text-green-600 bg-green-100';
    if (percentage >= 80) return 'text-blue-600 bg-blue-100';
    if (percentage >= 70) return 'text-yellow-600 bg-yellow-100';
    if (percentage >= 60) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Report Cards</h1>
          <p className="text-gray-600 mt-1">View academic performance and grades</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Report Card List */}
        <div className="lg:col-span-1">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Academic Terms</h2>
            <div className="space-y-2">
              {reportCards.map((report) => (
                <button
                  key={report.id}
                  onClick={() => setSelectedReport(report)}
                  className={`w-full text-left p-3 rounded-lg transition-colors ${
                    selectedReport?.id === report.id
                      ? 'bg-primary-50 border-2 border-primary-500'
                      : 'bg-gray-50 hover:bg-gray-100 border-2 border-transparent'
                  }`}
                >
                  <p className="font-medium text-sm">{report.term_label}</p>
                  <p className="text-xs text-gray-600">{report.academic_year}</p>
                  <p className="text-xs font-semibold text-primary-600 mt-1">
                    Avg: {report.average.toFixed(1)}%
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Report Card Details */}
        <div className="lg:col-span-3 space-y-6">
          {selectedReport && (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-blue-100">Total Marks</p>
                      <p className="text-3xl font-bold mt-2">{selectedReport.total}</p>
                    </div>
                    <div className="bg-white bg-opacity-20 p-3 rounded-lg">
                      <BookOpen className="w-6 h-6" />
                    </div>
                  </div>
                </div>
                <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-green-100">Average</p>
                      <p className="text-3xl font-bold mt-2">{selectedReport.average.toFixed(1)}%</p>
                    </div>
                    <div className="bg-white bg-opacity-20 p-3 rounded-lg">
                      <TrendingUp className="w-6 h-6" />
                    </div>
                  </div>
                </div>
                <div className="card bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-purple-100">Subjects</p>
                      <p className="text-3xl font-bold mt-2">{selectedReport.subjects.length}</p>
                    </div>
                    <div className="bg-white bg-opacity-20 p-3 rounded-lg">
                      <Award className="w-6 h-6" />
                    </div>
                  </div>
                </div>
              </div>

              {/* Subject Grades */}
              <div className="card">
                <h2 className="text-lg font-semibold mb-4">Subject Performance</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Subject
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Total Marks
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Max Marks
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Percentage
                        </th>
                        <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Grade
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Remarks
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {selectedReport.subjects.map((subject, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <BookOpen className="w-4 h-4 text-gray-400 mr-2" />
                              <span className="font-medium text-gray-900">{subject.subject}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                            {subject.total_mark}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center text-sm text-gray-900">
                            {subject.total_max}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getGradeColor(subject.percentage)}`}>
                              {subject.percentage.toFixed(1)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <span className="px-3 py-1 bg-gray-100 rounded-full text-sm font-semibold text-gray-900">
                              {subject.grade || 'N/A'}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {subject.remarks || '-'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
