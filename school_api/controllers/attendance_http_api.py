from odoo import http
from odoo.http import request
import json
import logging
from .cors_utils import add_cors_headers

_logger = logging.getLogger(__name__)


class AttendanceHTTPAPI(http.Controller):
    """Attendance API using HTTP with proper status codes"""
    
    # added for auth='public' case (it was auth='user' but changed to show proper unauthorized)
    # when auth='user' it redirects to login page, so i used auth='public' and manually check session
    def _check_session(self):
        """Check if user is authenticated, return JSON-RPC style error if not"""
        if not request.session.uid or request.session.uid == request.env.ref('base.public_user').id:
            return add_cors_headers(request.make_json_response({
                    'error': 'Unauthorized',
                    'message': 'Session Expired',
                    
            }, status=401))
        return None
    
    @http.route('/api/v2/attendance/student', type='http', auth='public', methods=['POST'], csrf=False)
    def get_student_attendance(self, **kwargs):
        """
        Get attendance records for a student
        Returns proper HTTP status codes (200, 400, 401, 403, 404, 500)
        
        Request Body (JSON):
        {
            "student_code": "STU001",
            "date_from": "2026-01-01",
            "date_to": "2026-02-14"
        }
        """
        try:
            # added for auth='public' case (it was auth='user' but changed to show proper unauthorized)
            # Check session first
            session_error = self._check_session()
            if session_error:
                return session_error
            
            # Parse JSON body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                return add_cors_headers(request.make_json_response({
                    'error': 'Invalid JSON',
                    'message': 'Request body must be valid JSON'
                }, status=400))
            
            # Check permissions - allow portal users to access their own data
            is_portal_user = request.env.user.has_group('base.group_portal')
            is_internal_user = request.env.user.has_group('base.group_user')
            
            if not (is_portal_user or is_internal_user):
                return add_cors_headers(request.make_json_response({
                    'error': 'Forbidden',
                    'message': 'Insufficient permissions'
                }, status=403))
            
            student_code = data.get('student_code')
            if not student_code:
                return add_cors_headers(request.make_json_response({
                    'error': 'Missing Parameter',
                    'message': 'student_code is required'
                }, status=400))
            
            student = request.env['school.student'].sudo().search([
                ('student_code', '=', student_code)
            ], limit=1)
            
            if not student:
                return add_cors_headers(request.make_json_response({
                    'error': 'Not Found',
                    'message': 'No student found with this code'
                }, status=404))
            
            # Portal users can only access their own data
            if is_portal_user:
                # Check if this student belongs to the logged-in user
                user_student = request.env['school.student'].sudo().search([
                    ('partner_id', '=', request.env.user.partner_id.id)
                ], limit=1)
                
                # Check if user is parent of this student
                user_parent = request.env['school.parent'].sudo().search([
                    ('partner_id', '=', request.env.user.partner_id.id)
                ], limit=1)
                
                has_access = False
                if user_student and user_student.id == student.id:
                    has_access = True
                elif user_parent and student in user_parent.student_ids:
                    has_access = True
                
                if not has_access:
                    return add_cors_headers(request.make_json_response({
                        'error': 'Forbidden',
                        'message': 'You can only access your own data'
                    }, status=403))
            
            domain = [('student_id', '=', student.id)]
            
            date_from = data.get('date_from')
            date_to = data.get('date_to')
            
            if date_from or date_to:
                attendance_domain = []
                if date_from:
                    attendance_domain.append(('date', '>=', date_from))
                if date_to:
                    attendance_domain.append(('date', '<=', date_to))
                
                attendances = request.env['school.attendance'].sudo().search(attendance_domain)
                if attendances:
                    domain.append(('attendance_id', 'in', attendances.ids))
            
            if 'school.attendance.line' in request.env:
                attendance_lines = request.env['school.attendance.line'].sudo().search(domain)
                
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
                
                return add_cors_headers(request.make_json_response({
                    'status': 'success',
                    'data': {
                        'student': {
                            'name': student.name,
                            'code': student.student_code
                        },
                        'records': attendance_list,
                        'summary': {
                            'total': total_days,
                            'present': present_days,
                            'absent': absent_days,
                            'late': len(attendance_lines.filtered(lambda r: r.status == 'late')),
                            'attendance_percentage': round((present_days / total_days * 100), 2) if total_days > 0 else 0
                        }
                    }
                }, status=200))
            else:
                return add_cors_headers(request.make_json_response({
                    'error': 'Not Available',
                    'message': 'Attendance module not installed'
                }, status=404))
        
        except Exception as e:
            _logger.error(f"Error in get_student_attendance: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))
