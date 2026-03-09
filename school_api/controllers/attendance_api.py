from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class AttendanceExternalAPI(http.Controller):
    
    def _validate_api_key(self):
        """Validate API key from request headers"""
        api_key = request.httprequest.headers.get('X-Api-Key')
        if not api_key:
            return False
        
        key_record = request.env['school.api.key'].sudo().search([
            ('key', '=', api_key),
            ('active', '=', True)
        ], limit=1)
        
        if key_record:
            key_record.sudo().write({
                'last_used': request.env.cr.now(),
                'usage_count': key_record.usage_count + 1
            })
            return True
        return False
    
    def _error_response(self, error, message, status=400):
        return {
            'status': 'error',
            'error': error,
            'message': message
        }
    
    @http.route('/api/v1/attendance/student', type='http', auth='none', methods=['POST'], csrf=False)
    def get_student_attendance(self, **kwargs):
        """
        Get attendance records for a student
        
        Request Body (raw JSON):
        {
            "student_code": "STU001",
            "date_from": "2026-01-01",
            "date_to": "2026-02-14"
        }
        """
        try:
            if not self._validate_api_key():
                return request.make_json_response(
                    self._error_response('Unauthorized', 'Invalid or missing API Key', 401)
                )
            
            # Parse JSON body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                return request.make_json_response(
                    self._error_response('Invalid JSON', 'Request body must be valid JSON')
                )
            
            student_code = data.get('student_code')
            if not student_code:
                return request.make_json_response(
                    self._error_response('Missing Parameter', 'student_code is required')
                )
            
            student = request.env['school.student'].sudo().search([
                ('student_code', '=', student_code)
            ], limit=1)
            
            if not student:
                return request.make_json_response(
                    self._error_response('Not Found', 'No student found with this code', 404)
                )
            
            # Build domain for attendance search
            # Attendance is stored in lines, not directly on attendance records
            domain = [('student_id', '=', student.id)]
            
            date_from = data.get('date_from')
            date_to = data.get('date_to')
            
            if date_from or date_to:
                # Need to search through attendance_id.date
                attendance_domain = []
                if date_from:
                    attendance_domain.append(('date', '>=', date_from))
                if date_to:
                    attendance_domain.append(('date', '<=', date_to))
                
                attendances = request.env['school.attendance'].sudo().search(attendance_domain)
                if attendances:
                    domain.append(('attendance_id', 'in', attendances.ids))
            
            # Check if attendance model exists
            if 'school.attendance.line' in request.env:
                attendance_lines = request.env['school.attendance.line'].sudo().search(domain)
                
                attendance_list = []
                for line in attendance_lines:
                    attendance_list.append({
                        'date': line.attendance_id.date.isoformat() if line.attendance_id.date else None,
                        'status': line.status,
                        'remarks': line.note or ''
                    })
                
                # Calculate statistics
                total_days = len(attendance_lines)
                present_days = len(attendance_lines.filtered(lambda r: r.status == 'present'))
                absent_days = len(attendance_lines.filtered(lambda r: r.status == 'absent'))
                
                return request.make_json_response({
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
                })
            else:
                return request.make_json_response(
                    self._error_response('Not Available', 'Attendance module not installed', 404)
                )
        
        except Exception as e:
            _logger.error(f"Error in get_student_attendance: {str(e)}")
            return request.make_json_response(
                self._error_response('Server Error', str(e), 500)
            )
