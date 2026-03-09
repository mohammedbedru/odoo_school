from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class StudentSessionAPI(http.Controller):
    """Student API using session authentication"""
    
    def _error_response(self, error, message, status=400):
        return {'status': status, 'error': error, 'message': message}
    
    @http.route('/api/student/profile', type='json', auth='user', methods=['POST'], csrf=False)
    def get_student_profile(self, **kwargs):
        """
        Get student profile information (session-based auth)
        
        Request Body:
        {
            "student_code": "STU001"
        }
        """
        try:
            student_code = kwargs.get('student_code')
            if not student_code:
                return self._error_response('Missing Parameter', 'student_code is required')
            
            student = request.env['school.student'].search([
                ('student_code', '=', student_code)
            ], limit=1)
            
            if not student:
                return self._error_response('Not Found', 'No student found with this code', 404)
            
            # Check access rights
            if not request.env.user.has_group('base.group_user'):
                return self._error_response('Forbidden', 'Insufficient permissions', 403)
            
            # Fetch fee stats
            fees = request.env['school.student.fee'].search([
                ('student_id', '=', student.id)
            ])
            
            fee_summary = {
                'total_fees': sum(fees.mapped('amount_total')),
                'paid_amount': sum(fees.filtered(lambda f: f.state == 'paid').mapped('amount_total')),
                'pending_amount': sum(fees.filtered(lambda f: f.state in ['draft', 'confirmed']).mapped('amount_total')),
                'overdue_count': len(fees.filtered(lambda f: f.state == 'overdue'))
            }
            
            parent_data = []
            for parent in student.parent_ids:
                parent_data.append({
                    'name': parent.name,
                    'email': parent.email,
                    'phone': parent.phone,
                })
            
            return {
                'status': 'success',
                'data': {
                    'name': student.name,
                    'code': student.student_code,
                    'grade': student.grade_id.name if student.grade_id else None,
                    'section': student.section_id.name if student.section_id else None,
                    'gender': student.gender,
                    'age': student.age,
                    'date_of_birth': student.dob.isoformat() if student.dob else None,
                    'email': student.email,
                    'phone': student.phone,
                    'parents': parent_data,
                    'fee_summary': fee_summary
                }
            }
        
        except Exception as e:
            _logger.error(f"Error in get_student_profile: {str(e)}")
            return self._error_response('Server Error', str(e), 500)
    
    @http.route('/api/student/list', type='json', auth='user', methods=['POST'], csrf=False)
    def list_students(self, **kwargs):
        """
        List students with optional filters
        
        Request Body:
        {
            "grade_id": 1,
            "section_id": 1,
            "limit": 50,
            "offset": 0
        }
        """
        try:
            if not request.env.user.has_group('base.group_user'):
                return self._error_response('Forbidden', 'Insufficient permissions', 403)
            
            domain = []
            grade_id = kwargs.get('grade_id')
            section_id = kwargs.get('section_id')
            limit = kwargs.get('limit', 50)
            offset = kwargs.get('offset', 0)
            
            if grade_id:
                domain.append(('grade_id', '=', grade_id))
            if section_id:
                domain.append(('section_id', '=', section_id))
            
            students = request.env['school.student'].search(domain, limit=limit, offset=offset)
            total_count = request.env['school.student'].search_count(domain)
            
            student_list = []
            for student in students:
                student_list.append({
                    'id': student.id,
                    'name': student.name,
                    'code': student.student_code,
                    'grade': student.grade_id.name if student.grade_id else None,
                    'section': student.section_id.name if student.section_id else None,
                    'email': student.email,
                })
            
            return {
                'status': 'success',
                'data': {
                    'students': student_list,
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }
        
        except Exception as e:
            _logger.error(f"Error in list_students: {str(e)}")
            return self._error_response('Server Error', str(e), 500)
