from odoo import http
from odoo.http import request
import json
import logging
from .cors_utils import add_cors_headers

_logger = logging.getLogger(__name__)


class FeeHTTPAPI(http.Controller):
    """Fee API using HTTP with proper status codes"""
    
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
    
    @http.route('/api/v2/fees/student', type='http', auth='public', methods=['POST'], csrf=False)
    def get_student_fees(self, **kwargs):
        """
        Get all fees for a student
        Returns proper HTTP status codes (200, 400, 401, 403, 404, 500)
        
        Request Body (JSON):
        {
            "student_code": "STU001"
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
            
            fees = request.env['school.student.fee'].sudo().search([
                ('student_id', '=', student.id)
            ])
            
            fee_list = []
            for fee in fees:
                term_label = dict(fee._fields['term'].selection).get(fee.term, fee.term)
                
                fee_list.append({
                    'id': fee.id,
                    'display_name': fee.display_name,
                    'academic_year': fee.academic_year_id.name if fee.academic_year_id else None,
                    'term': term_label,
                    'amount_total': fee.amount_total,
                    'amount_paid': fee.amount_paid,
                    'amount_due': fee.amount_due,
                    'state': fee.state,
                    'payment_state': fee.payment_state,
                    'due_date': fee.due_date.isoformat() if fee.due_date else None,
                })
            
            return add_cors_headers(request.make_json_response({
                'status': 'success',
                'data': {
                    'student': {
                        'name': student.name,
                        'code': student.student_code
                    },
                    'fees': fee_list,
                    'summary': {
                        'total': sum(fees.mapped('amount_total')),
                        'paid': sum(fees.mapped('amount_paid')),
                        'due': sum(fees.mapped('amount_due'))
                    }
                }
            }, status=200))
        
        except Exception as e:
            _logger.error(f"Error in get_student_fees: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return add_cors_headers(request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500))
