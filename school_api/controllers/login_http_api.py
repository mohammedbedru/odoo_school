from odoo import http
from odoo.http import request
import json
import logging
from .cors_utils import add_cors_headers

_logger = logging.getLogger(__name__)


class AuthHTTPAPI(http.Controller):
    """Authentication API using HTTP with proper status codes"""

    @http.route('/api/v2/auth/login', type='http', auth='none', methods=['POST'], csrf=False)
    def api_login(self, **kwargs):
        """
        Login and create session
        Returns proper HTTP status codes (200, 400, 401, 500)
        
        Request Body (JSON):
        {
            "db": "odoo18",
            "login": "admin",
            "password": "admin"
        }
        
        Response (HTTP 200):
        {
            "status": "success",
            "session_id": "...",
            "uid": 2,
            "name": "Admin User",
            "is_student": false,
            "student_id": false,
            "company_name": "My Company"
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
            
            # Get credentials
            db = data.get('db')
            login = data.get('login')
            password = data.get('password')

            if not login or not password:
                return add_cors_headers(request.make_json_response({
                    'error': 'Missing Credentials',
                    'message': 'login and password are required'
                }, status=400))

            # Use provided db or get from request context
            database = db or request.session.db or request.db
            
            if not database:
                return add_cors_headers(request.make_json_response({
                    'error': 'Database Not Specified',
                    'message': 'Database name is required'
                }, status=400))

            # Authenticate
            credential = {
                'type': 'password',
                'login': login,
                'password': password
            }
            
            try:
                auth_info = request.session.authenticate(database, credential)
                uid = auth_info.get('uid')
            except Exception as auth_error:
                _logger.warning(f"Authentication failed for user {login}: {str(auth_error)}")
                return add_cors_headers(request.make_json_response({
                    'error': 'Authentication Failed',
                    'message': 'Invalid username or password'
                }, status=401))
            
            if not uid:
                return add_cors_headers(request.make_json_response({
                    'error': 'Authentication Failed',
                    'message': 'Invalid username or password'
                }, status=401))

            # Fetch user/student info
            user = request.env['res.users'].sudo().browse(uid)
            
            # Check if user is linked to a student
            student = request.env['school.student'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)
            
            # If not a student, check if they're a parent
            student_code = None
            student_id = None
            is_student = False
            is_parent = False
            students = []
            
            if student:
                is_student = True
                student_id = student.id
                student_code = student.student_code
                students = [{
                    'id': student.id,
                    'code': student.student_code,
                    'name': student.name,
                    'grade': student.grade_id.name if student.grade_id else None,
                }]
            else:
                # Check if user is a parent
                parent = request.env['school.parent'].sudo().search([
                    ('partner_id', '=', user.partner_id.id)
                ], limit=1)
                if parent and parent.student_ids:
                    is_parent = True
                    # Get all students for parent
                    for child in parent.student_ids:
                        students.append({
                            'id': child.id,
                            'code': child.student_code,
                            'name': child.name,
                            'grade': child.grade_id.name if child.grade_id else None,
                        })
                    # Set first student as default
                    first_student = parent.student_ids[0]
                    student_id = first_student.id
                    student_code = first_student.student_code

            return add_cors_headers(request.make_json_response({
                'status': 'success',
                'session_id': request.session.sid,
                'uid': uid,
                'name': user.name,
                'login': user.login,
                'is_student': is_student,
                'is_parent': is_parent,
                'student_id': student_id,
                'student_code': student_code,
                'students': students,
                'company_name': user.company_id.name
            }, status=200))

        except Exception as e:
            _logger.error(f"Error in api_login: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))

    @http.route('/api/v2/auth/logout', type='http', auth='user', methods=['POST'], csrf=False)
    def api_logout(self, **kwargs):
        """
        Logout and destroy session
        Returns proper HTTP status codes (200, 401, 500)
        
        Response (HTTP 200):
        {
            "status": "success",
            "message": "Logged out successfully"
        }
        """
        try:
            request.session.logout()
            return add_cors_headers(request.make_json_response({
                'status': 'success',
                'message': 'Logged out successfully'
            }, status=200))
        except Exception as e:
            _logger.error(f"Error in api_logout: {str(e)}")
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))
    
    @http.route('/api/v2/auth/check', type='http', auth='user', methods=['GET', 'POST'], csrf=False)
    def check_session(self, **kwargs):
        """
        Check if session is valid
        Returns proper HTTP status codes (200, 401)
        
        Response (HTTP 200):
        {
            "status": "authenticated",
            "uid": 2,
            "name": "Admin User",
            "login": "admin"
        }
        """
        try:
            if request.env.uid:
                user = request.env.user
                
                # Check if user is linked to a student
                student = request.env['school.student'].sudo().search([
                    ('partner_id', '=', user.partner_id.id)
                ], limit=1)
                
                # If not a student, check if they're a parent
                student_code = None
                student_id = None
                is_student = False
                is_parent = False
                students = []
                
                if student:
                    is_student = True
                    student_id = student.id
                    student_code = student.student_code
                    students = [{
                        'id': student.id,
                        'code': student.student_code,
                        'name': student.name,
                        'grade': student.grade_id.name if student.grade_id else None,
                    }]
                else:
                    # Check if user is a parent
                    parent = request.env['school.parent'].sudo().search([
                        ('partner_id', '=', user.partner_id.id)
                    ], limit=1)
                    if parent and parent.student_ids:
                        is_parent = True
                        # Get all students for parent
                        for child in parent.student_ids:
                            students.append({
                                'id': child.id,
                                'code': child.student_code,
                                'name': child.name,
                                'grade': child.grade_id.name if child.grade_id else None,
                            })
                        # Set first student as default
                        first_student = parent.student_ids[0]
                        student_id = first_student.id
                        student_code = first_student.student_code
                
                return add_cors_headers(request.make_json_response({
                    'status': 'authenticated',
                    'uid': user.id,
                    'name': user.name,
                    'login': user.login,
                    'is_student': is_student,
                    'is_parent': is_parent,
                    'student_id': student_id,
                    'student_code': student_code,
                    'students': students,
                    'company_name': user.company_id.name
                }, status=200))
            else:
                return add_cors_headers(request.make_json_response({
                    'error': 'Not Authenticated',
                    'message': 'No valid session found'
                }, status=401))
        except Exception as e:
            _logger.error(f"Error in check_session: {str(e)}")
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))

    @http.route('/api/v2/auth/<path:path>', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def options_auth(self, **kwargs):
        """Handle OPTIONS preflight requests for auth endpoints"""
        return add_cors_headers(request.make_response('', headers=[
            ('Content-Type', 'text/plain'),
        ]))
