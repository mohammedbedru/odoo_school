from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)

# doesnt work
class PaymentAPI(http.Controller):
    """
    Payment API with API Key authentication
    Requires X-Api-Key header for authentication
    """
    
    def _validate_api_key(self):
        """Validate API key from request header"""
        api_key = request.httprequest.headers.get('X-Api-Key')
        
        if not api_key:
            return None
        
        # Search for valid API key
        key_record = request.env['school.api.key'].sudo().search([
            ('key', '=', api_key),
            ('active', '=', True)
        ], limit=1)
        
        if key_record:
            # Log usage
            key_record.sudo().write({
                'last_used': fields.Date.today(),
                'usage_count': key_record.usage_count + 1
            })
            _logger.info(f"API Key validated: {key_record.name}")
            return key_record
        
        _logger.warning(f"Invalid API key attempted")
        return None
    
    def _error_response(self, error, message, status=400):
        return {
            'status': 'error',
            'error': error,
            'message': message
        }
    
    @http.route('/api/v1/fees/payment/record', type='http', auth='none', methods=['POST'], csrf=False)
    def record_payment(self, **kwargs):
        """
        Record a payment for a fee with full reconciliation
        
        Authentication: API Key via X-Api-Key header
        
        Request Body (raw JSON):
        {
            "fee_id": 123,
            "amount": 5000.00,
            "payment_reference": "PAY123456",
            "payment_date": "2026-02-14"
        }
        """
        try:
            # Validate API key
            api_key_record = self._validate_api_key()
            if not api_key_record:
                return request.make_json_response(
                    self._error_response('Unauthorized', 'Invalid or missing API key', 401)
                )
            
            # Parse JSON body
            try:
                data = json.loads(request.httprequest.data.decode('utf-8'))
            except:
                return request.make_json_response(
                    self._error_response('Invalid JSON', 'Request body must be valid JSON')
                )
            
            fee_id = data.get('fee_id')
            amount = data.get('amount')
            payment_reference = data.get('payment_reference')
            payment_date = data.get('payment_date')
            
            if not all([fee_id, amount, payment_reference]):
                return request.make_json_response(
                    self._error_response('Missing Parameters', 'fee_id, amount, and payment_reference are required')
                )
            
            # Use sudo for operations with company context
            fee = request.env['school.student.fee'].sudo().browse(fee_id)
            if not fee.exists():
                return request.make_json_response(
                    self._error_response('Not Found', 'Fee record not found', 404)
                )
            
            # Check if invoice exists, generate if not
            if not fee.invoice_id:
                fee.action_generate_invoice()
            
            invoice = fee.invoice_id
            if not invoice:
                return request.make_json_response(
                    self._error_response('Invoice Error', 'Could not generate invoice')
                )
            
            # Check if already paid
            if invoice.payment_state == 'paid':
                return request.make_json_response(
                    self._error_response('Already Paid', 'This invoice is already fully paid')
                )
            
            # Get bank journal
            journal = request.env['account.journal'].sudo().search([
                ('type', '=', 'bank'),
                ('company_id', '=', invoice.company_id.id)
            ], limit=1)
            
            if not journal:
                return request.make_json_response(
                    self._error_response('Configuration Error', 'No bank journal found')
                )
            
            # Use payment register wizard with company context
            payment_wizard = request.env['account.payment.register'].sudo().with_context(
                active_model='account.move',
                active_ids=invoice.ids,
                allowed_company_ids=[invoice.company_id.id]
            ).create({
                'amount': float(amount),
                'payment_date': payment_date or fields.Date.today(),
                'journal_id': journal.id,
            })
            
            # Create and post payment
            payment_result = payment_wizard.action_create_payments()
            
            # Get created payment
            if payment_result and 'res_id' in payment_result:
                payment = request.env['account.payment'].sudo().browse(payment_result['res_id'])
                if payment:
                    payment.write({'ref': payment_reference})
                
                return request.make_json_response({
                    'status': 'success',
                    'message': 'Payment recorded and reconciled successfully',
                    'data': {
                        'fee_id': fee.id,
                        'invoice_id': invoice.id,
                        'invoice_number': invoice.name,
                        'payment_id': payment.id,
                        'payment_name': payment.name,
                        'amount_paid': amount,
                        'invoice_payment_state': invoice.payment_state,
                        'invoice_amount_residual': invoice.amount_residual,
                        'payment_reference': payment_reference
                    }
                })
            else:
                return request.make_json_response(
                    self._error_response('Payment Error', 'Payment created but could not retrieve details')
                )
        
        except Exception as e:
            _logger.error(f"Error in record_payment: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return request.make_json_response(
                self._error_response('Server Error', str(e), 500)
            )
