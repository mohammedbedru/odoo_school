from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)


class FeeSessionAPI(http.Controller):
    """Fee API using session authentication"""
    
    def _error_response(self, error, message, status=400):
        return {'status': status, 'error': error, 'message': message}
    
    @http.route('/api/fees/student', type='json', auth='user', methods=['POST'], csrf=False)
    def get_student_fees(self, **kwargs):
        """
        Get all fees for a student (session-based auth)
        
        Request Body:
        {
            "student_code": "STU001"
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
            
            fees = request.env['school.student.fee'].search([
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
            
            return {
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
            }
        
        except Exception as e:
            _logger.error(f"Error in get_student_fees: {str(e)}")
            return self._error_response('Server Error', str(e), 500)
