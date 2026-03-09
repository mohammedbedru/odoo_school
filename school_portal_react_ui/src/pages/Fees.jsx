import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { feeAPI } from '../services/api';
import { DollarSign, CreditCard, Download, CheckCircle, XCircle } from 'lucide-react';
import { formatCurrency, formatDate, getPaymentStateColor, getPaymentStateLabel } from '../utils/helpers';

export default function Fees() {
  const { selectedStudent } = useAuth();
  const [loading, setLoading] = useState(true);
  const [fees, setFees] = useState(null);
  const [selectedFee, setSelectedFee] = useState(null);
  const [paymentModal, setPaymentModal] = useState(false);
  const [paymentForm, setPaymentForm] = useState({
    amount: '',
    reference: '',
    date: new Date().toISOString().split('T')[0],
  });
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    loadFees();
  }, [selectedStudent]);

  const loadFees = async () => {
    try {
      setLoading(true);
      if (selectedStudent) {
        const response = await feeAPI.getStudentFees(selectedStudent);
        setFees(response);
      }
    } catch (error) {
      console.error('Error loading fees:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (e) => {
    e.preventDefault();
    setProcessing(true);
    
    try {
      await feeAPI.recordPayment(
        selectedFee.id,
        parseFloat(paymentForm.amount),
        paymentForm.reference,
        paymentForm.date
      );
      
      alert('Payment recorded successfully!');
      setPaymentModal(false);
      setSelectedFee(null);
      setPaymentForm({ amount: '', reference: '', date: new Date().toISOString().split('T')[0] });
      loadFees();
    } catch (error) {
      alert('Payment failed: ' + (error.response?.data?.message || error.message));
    } finally {
      setProcessing(false);
    }
  };

  const openPaymentModal = (fee) => {
    setSelectedFee(fee);
    setPaymentForm({
      ...paymentForm,
      amount: fee.amount_due.toString(),
    });
    setPaymentModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-gradient-to-br from-blue-500 to-blue-600 text-white">
          <p className="text-blue-100">Total Fees</p>
          <p className="text-3xl font-bold mt-2">{formatCurrency(fees?.data?.summary?.total || 0)}</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500 to-green-600 text-white">
          <p className="text-green-100">Paid</p>
          <p className="text-3xl font-bold mt-2">{formatCurrency(fees?.data?.summary?.paid || 0)}</p>
        </div>
        <div className="card bg-gradient-to-br from-red-500 to-red-600 text-white">
          <p className="text-red-100">Due</p>
          <p className="text-3xl font-bold mt-2">{formatCurrency(fees?.data?.summary?.due || 0)}</p>
        </div>
      </div>

      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Fee Records</h2>
        <div className="space-y-4">
          {fees?.data?.fees?.map((fee) => (
            <div key={fee.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{fee.display_name}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {fee.academic_year} - {fee.term}
                  </p>
                  {fee.due_date && (
                    <p className="text-sm text-gray-600 mt-1">
                      Due: {formatDate(fee.due_date)}
                    </p>
                  )}
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getPaymentStateColor(fee.payment_state)}`}>
                  {getPaymentStateLabel(fee.payment_state)}
                </span>
              </div>
              
              <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t">
                <div>
                  <p className="text-sm text-gray-600">Total Amount</p>
                  <p className="font-semibold">{formatCurrency(fee.amount_total)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Paid</p>
                  <p className="font-semibold text-green-600">{formatCurrency(fee.amount_paid)}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Due</p>
                  <p className="font-semibold text-red-600">{formatCurrency(fee.amount_due)}</p>
                </div>
              </div>

              {fee.amount_due > 0 && (
                <button
                  onClick={() => openPaymentModal(fee)}
                  className="mt-4 btn-primary w-full flex items-center justify-center gap-2"
                >
                  <CreditCard className="w-4 h-4" />
                  Pay Now
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {paymentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <h3 className="text-xl font-semibold mb-4">Record Payment</h3>
            <form onSubmit={handlePayment} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Amount</label>
                <input
                  type="number"
                  step="0.01"
                  value={paymentForm.amount}
                  onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
                  className="input"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Payment Reference</label>
                <input
                  type="text"
                  value={paymentForm.reference}
                  onChange={(e) => setPaymentForm({ ...paymentForm, reference: e.target.value })}
                  className="input"
                  placeholder="e.g., CHK123456"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Payment Date</label>
                <input
                  type="date"
                  value={paymentForm.date}
                  onChange={(e) => setPaymentForm({ ...paymentForm, date: e.target.value })}
                  className="input"
                  required
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setPaymentModal(false);
                    setSelectedFee(null);
                  }}
                  className="flex-1 btn-secondary"
                  disabled={processing}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 btn-primary"
                  disabled={processing}
                >
                  {processing ? 'Processing...' : 'Submit Payment'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
