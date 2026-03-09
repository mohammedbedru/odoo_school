from odoo import http
from odoo.http import request
import json
import logging
from .cors_utils import add_cors_headers

_logger = logging.getLogger(__name__)


class GradesHTTPAPI(http.Controller):
    """Grades/Report Card API using HTTP with proper status codes"""
    
    def _check_session(self):
        """Check if user is authenticated"""
        if not request.session.uid or request.session.uid == request.env.ref('base.public_user').id:
            return add_cors_headers(request.make_json_response({
                'error': 'Unauthorized',
                'message': 'Session Expired',
            }, status=401))
        return None
    
    @http.route('/api/v2/grades/student', type='http', auth='public', methods=['POST'], csrf=False)
    def get_student_grades(self, **kwargs):
        """
        Get report cards/grades for a student
        Returns proper HTTP status codes (200, 400, 401, 403, 404, 500)
        
        Request Body (JSON):
        {
            "student_code": "STU001",
            "academic_year_id": 1,  // optional
            "term": "t1"  // optional
        }
        """
        try:
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
                user_student = request.env['school.student'].sudo().search([
                    ('partner_id', '=', request.env.user.partner_id.id)
                ], limit=1)
                
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
            
            # Build domain for report cards
            domain = [('student_id', '=', student.id)]
            
            academic_year_id = data.get('academic_year_id')
            term = data.get('term')
            
            if academic_year_id:
                domain.append(('academic_year_id', '=', academic_year_id))
            if term:
                domain.append(('term', '=', term))
            
            # Only show published report cards to portal users
            if is_portal_user:
                domain.append(('state', '=', 'published'))
            
            report_cards = request.env['school.report.card'].sudo().search(domain, order='academic_year_id desc, term')
            
            report_list = []
            for report in report_cards:
                term_label = dict(report._fields['term'].selection).get(report.term, report.term)
                
                # Get subject lines
                subjects = []
                for line in report.line_ids:
                    subjects.append({
                        'subject': line.subject_id.name if line.subject_id else None,
                        'total_mark': line.total_mark,
                        'total_max': line.total_max,
                        'percentage': line.percentage,
                        'grade': line.grade,
                        'remarks': line.remark or '',
                        'quiz_mark': line.quiz_mark,
                        'mid_mark': line.mid_mark,
                        'final_mark': line.final_mark,
                        'assignment_mark': line.assignment_mark,
                    })
                
                report_list.append({
                    'id': report.id,
                    'name': report.name,
                    'academic_year': report.academic_year_id.name if report.academic_year_id else None,
                    'term': term,
                    'term_label': term_label,
                    'total': report.total,
                    'average': report.average,
                    'state': report.state,
                    'subjects': subjects,
                })
            
            return add_cors_headers(request.make_json_response({
                'status': 'success',
                'data': {
                    'student': {
                        'name': student.name,
                        'code': student.student_code
                    },
                    'report_cards': report_list,
                }
            }, status=200))
        
        except Exception as e:
            _logger.error(f"Error in get_student_grades: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))
    
    @http.route('/api/v2/grades/<path:path>', type='http', auth='none', methods=['OPTIONS'], csrf=False)
    def options_grades(self, **kwargs):
        """Handle OPTIONS preflight requests for grades endpoints"""
        return add_cors_headers(request.make_response('', headers=[
            ('Content-Type', 'text/plain'),
        ]))
