from odoo import http
from odoo.http import request
import json
import logging
from .cors_utils import add_cors_headers

_logger = logging.getLogger(__name__)


class StudentHTTPAPI(http.Controller):
    """Student API using HTTP with proper status codes"""
    
    @http.route('/api/v2/student/profile', type='http', auth='user', methods=['POST'], csrf=False)
    def get_student_profile(self, **kwargs):
        """
        Get student profile information
        Returns proper HTTP status codes (200, 400, 403, 404, 500)
        
        Request Body (JSON):
        {
            "student_code": "STU001"
        }
        """
        try:
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
            
            # Fetch fee stats
            fees = request.env['school.student.fee'].sudo().search([
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
                    'relation': parent.relation,
                })
            
            return add_cors_headers(request.make_json_response({
                'status': 'success',
                'data': {
                    'name': student.name,
                    'code': student.student_code,
                    'grade': student.grade_id.name if student.grade_id else None,
                    'section': student.section_id.name if student.section_id else None,
                    'gender': student.gender,
                    'age': student.age,
                    'date_of_birth': student.dob.isoformat() if student.dob else None,
                    'admission_date': student.admission_date.isoformat() if student.admission_date else None,
                    'email': student.email,
                    'phone': student.phone,
                    'address': student.address,
                    'state': student.status,
                    'photo_url': f'/web/image/school.student/{student.id}/photo' if student.photo else None,
                    'parent_ids': parent_data,
                    'fee_summary': fee_summary
                }
            }, status=200))
        
        except Exception as e:
            _logger.error(f"Error in get_student_profile: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))
    
    @http.route('/api/v2/student/list', type='http', auth='user', methods=['POST'], csrf=False)
    def list_students(self, **kwargs):
        """
        List students with optional filters
        Returns proper HTTP status codes (200, 403, 500)
        
        Request Body (JSON):
        {
            "grade_id": 1,
            "section_id": 1,
            "limit": 50,
            "offset": 0
        }
        """
        try:
            # Parse JSON body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                data = {}
            
            # Check permissions - only internal users can list students
            if not request.env.user.has_group('base.group_user'):
                return add_cors_headers(request.make_json_response({
                    'error': 'Forbidden',
                    'message': 'Insufficient permissions'
                }, status=403))
            
            domain = []
            grade_id = data.get('grade_id')
            section_id = data.get('section_id')
            limit = data.get('limit', 50)
            offset = data.get('offset', 0)
            
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
            
            return add_cors_headers(request.make_json_response({
                'status': 'success',
                'data': {
                    'students': student_list,
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            }, status=200))
        
        except Exception as e:
            _logger.error(f"Error in list_students: {str(e)}")
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))
    
    @http.route('/api/v2/student/<path:path>', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def options_student(self, **kwargs):
        """Handle OPTIONS preflight requests for student endpoints"""
        return add_cors_headers(request.make_response('', headers=[
            ('Content-Type', 'text/plain'),
        ]))
