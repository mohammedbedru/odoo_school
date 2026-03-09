from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class StudentExternalAPI(http.Controller):
    
    def _validate_api_key(self):
        """Validate API key from request headers"""
        api_key = request.httprequest.headers.get('X-Api-Key')
        if not api_key:
            return False
        
        # Check if API key exists and is active
        key_record = request.env['school.api.key'].sudo().search([
            ('key', '=', api_key),
            ('active', '=', True)
        ], limit=1)
        
        if key_record:
            # Log API usage
            key_record.sudo().write({
                'last_used': request.env.cr.now(),
                'usage_count': key_record.usage_count + 1
            })
            return True
        return False
    
    def _error_response(self, error, message, status=400):
        """Standard error response format"""
        return {
            'status': 'error',
            'error': error,
            'message': message
        }
    
    @http.route('/api/v1/student/profile', type='http', auth='none', methods=['POST'], csrf=False)
    def get_student_profile(self, **kwargs):
        """
        Get student profile information
        
        Request Body (raw JSON):
        {
            "student_code": "STU001"
        }
        
        Headers:
        X-Api-Key: your_api_key_here
        Content-Type: application/json
        """
        try:
            # Log incoming request
            _logger.info(f"=== API Request to /api/v1/student/profile ===")
            _logger.info(f"Headers: {dict(request.httprequest.headers)}")
            _logger.info(f"Raw Body: {request.httprequest.data}")
            
            # 1. Security Check
            if not self._validate_api_key():
                return request.make_json_response(
                    self._error_response('Unauthorized', 'Invalid or missing API Key', 401)
                )
            
            # 2. Parse JSON body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
                _logger.info(f"Parsed JSON: {data}")
            except Exception as parse_error:
                _logger.error(f"JSON Parse Error: {str(parse_error)}")
                return request.make_json_response(
                    self._error_response('Invalid JSON', 'Request body must be valid JSON')
                )
            
            # 3. Get Parameters
            student_code = data.get('student_code')
            if not student_code:
                return request.make_json_response(
                    self._error_response('Missing Parameter', 'student_code is required')
                )
            
            # 4. Search for Student
            student = request.env['school.student'].sudo().search([
                ('student_code', '=', student_code)
            ], limit=1)
            
            if not student:
                return request.make_json_response(
                    self._error_response('Not Found', 'No student found with this code', 404)
                )
            
            # 5. Fetch Fee Stats
            fees = request.env['school.student.fee'].sudo().search([
                ('student_id', '=', student.id)
            ])
            
            fee_summary = {
                'total_fees': sum(fees.mapped('amount_total')),
                'paid_amount': sum(fees.filtered(lambda f: f.state == 'paid').mapped('amount_total')),
                'pending_amount': sum(fees.filtered(lambda f: f.state in ['draft', 'confirmed']).mapped('amount_total')),
                'overdue_count': len(fees.filtered(lambda f: f.state == 'overdue'))
            }
            
            # 6. Build Response
            parent_data = []
            for parent in student.parent_ids:
                parent_data.append({
                    'name': parent.name,
                    'email': parent.email,
                    'phone': parent.phone,
                })
            
            return request.make_json_response({
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
            })
        
        except Exception as e:
            _logger.error(f"Error in get_student_profile: {str(e)}")
            return request.make_json_response(
                self._error_response('Server Error', str(e), 500)
            )
    
    @http.route('/api/v1/student/list', type='http', auth='none', methods=['POST'], csrf=False)
    def list_students(self, **kwargs):
        """
        List students with optional filters
        
        Request Body (raw JSON):
        {
            "grade_id": 1,
            "section_id": 1,
            "limit": 50,
            "offset": 0
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
                data = {}
            
            domain = []
            grade_id = data.get('grade_id')
            section_id = data.get('section_id')
            limit = data.get('limit', 50)
            offset = data.get('offset', 0)
            
            if grade_id:
                domain.append(('grade_id', '=', grade_id))
            if section_id:
                domain.append(('section_id', '=', section_id))
            
            students = request.env['school.student'].sudo().search(domain, limit=limit, offset=offset)
            total_count = request.env['school.student'].sudo().search_count(domain)
            
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
            
            return request.make_json_response({
                'status': 'success',
                'data': {
                    'students': student_list,
                    'total_count': total_count,
                    'limit': limit,
                    'offset': offset
                }
            })
        
        except Exception as e:
            _logger.error(f"Error in list_students: {str(e)}")
            return request.make_json_response(
                self._error_response('Server Error', str(e), 500)
            )
