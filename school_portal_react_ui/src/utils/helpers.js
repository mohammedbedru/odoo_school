import { format, parseISO } from 'date-fns';

export const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    return format(parseISO(dateString), 'MMM dd, yyyy');
  } catch {
    return dateString;
  }
};

export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
};

export const getPaymentStateColor = (state) => {
  const colors = {
    paid: 'text-green-600 bg-green-100',
    partial: 'text-yellow-600 bg-yellow-100',
    not_paid: 'text-red-600 bg-red-100',
    draft: 'text-gray-600 bg-gray-100',
  };
  return colors[state] || 'text-gray-600 bg-gray-100';
};

export const getPaymentStateLabel = (state) => {
  const labels = {
    paid: 'Paid',
    partial: 'Partially Paid',
    not_paid: 'Unpaid',
    draft: 'Draft',
  };
  return labels[state] || state;
};

export const calculateAttendancePercentage = (present, total) => {
  if (total === 0) return 0;
  return Math.round((present / total) * 100);
};

export const getAttendanceColor = (status) => {
  // If status is a number (percentage), use the old logic
  if (typeof status === 'number') {
    if (status >= 90) return 'text-green-600';
    if (status >= 75) return 'text-yellow-600';
    return 'text-red-600';
  }
  
  // If status is a string (attendance status)
  const colors = {
    present: 'text-green-600 bg-green-100',
    absent: 'text-red-600 bg-red-100',
    late: 'text-yellow-600 bg-yellow-100',
    excused: 'text-blue-600 bg-blue-100',
  };
  return colors[status?.toLowerCase()] || 'text-gray-600 bg-gray-100';
};
