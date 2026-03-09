from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class FeeExternalAPI(http.Controller):
    
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
    
    @http.route('/api/v1/fees/student', type='http', auth='none', methods=['POST'], csrf=False)
    def get_student_fees(self, **kwargs):
        """
        Get all fees for a student
        
        Request Body (raw JSON):
        {
            "student_code": "STU001"
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
            
            fees = request.env['school.student.fee'].sudo().search([
                ('student_id', '=', student.id)
            ])
            
            fee_list = []
            for fee in fees:
                # Get term label from selection field
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
            
            return request.make_json_response({
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
            })
        
        except Exception as e:
            _logger.error(f"Error in get_student_fees: {str(e)}")
            return request.make_json_response(
                self._error_response('Server Error', str(e), 500)
            )
    