from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class AttendanceSessionAPI(http.Controller):
    """Attendance API using session authentication"""
    
    def _error_response(self, error, message, status=400):
        return {'status': status, 'error': error, 'message': message}
    
    @http.route('/api/attendance/student', type='json', auth='user', methods=['POST'], csrf=False)
    def get_student_attendance(self, **kwargs):
        """
        Get attendance records for a student (session-based auth)
        
        Request Body:
        {
            "student_code": "STU001",
            "date_from": "2026-01-01",
            "date_to": "2026-02-14"
        }
        """
        try:
            if not request.env.user.has_group('base.group_user'):
                return self._error_response('Forbidden', 'Insufficient permissions', 403)
            
            student_code = kwargs.get('student_code')
            if not student_code:
                return self._error_response('Missing Parameter', 'student_code is required')
            
            student = request.env['school.student'].search([
                ('student_code', '=', student_code)
            ], limit=1)
            
            if not student:
                return self._error_response('Not Found', 'No student found with this code', 404)
            
            domain = [('student_id', '=', student.id)]
            
            date_from = kwargs.get('date_from')
            date_to = kwargs.get('date_to')
            
            if date_from or date_to:
                attendance_domain = []
                if date_from:
                    attendance_domain.append(('date', '>=', date_from))
                if date_to:
                    attendance_domain.append(('date', '<=', date_to))
                
                attendances = request.env['school.attendance'].search(attendance_domain)
                if attendances:
                    domain.append(('attendance_id', 'in', attendances.ids))
            
            if 'school.attendance.line' in request.env:
                attendance_lines = request.env['school.attendance.line'].search(domain)
                
                attendance_list = []
                for line in attendance_lines:
                    attendance_list.append({
                        'date': line.attendance_id.date.isoformat() if line.attendance_id.date else None,
                        'status': line.status,
                        'remarks': line.note or ''
                    })
                
                total_days = len(attendance_lines)
                present_days = len(attendance_lines.filtered(lambda r: r.status == 'present'))
                absent_days = len(attendance_lines.filtered(lambda r: r.status == 'absent'))
                
                return {
                    'status': 'success',
                    'data': {
                        'student': {
                            'name': student.name,
                            'code': student.student_code
                        },
                        'attendance': attendance_list,
                        'summary': {
                            'total_days': total_days,
                            'present': present_days,
                            'absent': absent_days,
                            'attendance_percentage': round((present_days / total_days * 100), 2) if total_days > 0 else 0
                        }
                    }
                }
            else:
                return self._error_response('Not Available', 'Attendance module not installed', 404)
        
        except Exception as e:
            _logger.error(f"Error in get_student_attendance: {str(e)}")
            return self._error_response('Server Error', str(e), 500)
