from odoo import http, fields
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class PaymentHTTPAPI(http.Controller):
    """Payment API using HTTP with proper status codes"""

    # added for auth='public' case (it was auth='user' but changed to show proper unauthorized)    
    # when auth='user' it redirects to login page, so i used auth='public' and manually check session
    def _check_session(self):
        """Check if user is authenticated, return JSON-RPC style error if not"""
        if not request.session.uid or request.session.uid == request.env.ref('base.public_user').id:
            return request.make_json_response({
                'error': 'Unauthorized',
                'message': 'Session Expired',
            }, status=401)
        return None
    
    @http.route('/api/v2/fees/payment/record', type='http', auth='public', methods=['POST'], csrf=False)
    def record_payment(self, **kwargs):
        """
        Record a payment for a fee with full reconciliation
        Returns proper HTTP status codes (200, 400, 401, 403, 404, 500)
        
        Request Body (JSON):
        {
            "fee_id": 123,
            "amount": 5000.00,
            "payment_reference": "PAY123456",
            "payment_date": "2026-02-14",
            "journal_id": 5
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
                return request.make_json_response({
                    'error': 'Invalid JSON',
                    'message': 'Request body must be valid JSON'
                }, status=400)
            
            # Check permissions
            if not request.env.user.has_group('base.group_user'):
                return request.make_json_response({
                    'error': 'Forbidden',
                    'message': 'Insufficient permissions'
                }, status=403)
            
            # Get parameters
            fee_id = data.get('fee_id')
            amount = data.get('amount')
            payment_reference = data.get('payment_reference')
            payment_date = data.get('payment_date')
            journal_id = data.get('journal_id')
            
            # Validate required parameters
            if not all([fee_id, amount, payment_reference]):
                return request.make_json_response({
                    'error': 'Missing Parameters',
                    'message': 'fee_id, amount, and payment_reference are required'
                }, status=400)
            
            # Get fee record
            fee = request.env['school.student.fee'].browse(fee_id)
            if not fee.exists():
                return request.make_json_response({
                    'error': 'Not Found',
                    'message': 'Fee record not found'
                }, status=404)
            
            _logger.info(f"Processing payment for fee {fee_id}, amount: {amount}")
            
            # Step 1: Generate invoice if not exists
            if not fee.invoice_id:
                _logger.info(f"No invoice found for fee {fee_id}, generating...")
                try:
                    fee.action_generate_invoice()
                    _logger.info(f"Invoice generated: {fee.invoice_id.name}")
                except Exception as e:
                    _logger.error(f"Failed to generate invoice: {str(e)}")
                    return request.make_json_response({
                        'error': 'Invoice Generation Failed',
                        'message': str(e)
                    }, status=500)
            
            invoice = fee.invoice_id
            if not invoice:
                return request.make_json_response({
                    'error': 'Invoice Error',
                    'message': 'Could not generate or retrieve invoice'
                }, status=500)
            
            # Step 2: Post invoice if in draft state
            if invoice.state == 'draft':
                try:
                    invoice.action_post()
                    _logger.info(f"Invoice {invoice.name} posted")
                except Exception as e:
                    _logger.error(f"Failed to post invoice: {str(e)}")
                    return request.make_json_response({
                        'error': 'Invoice Posting Failed',
                        'message': str(e)
                    }, status=500)
            
            # Step 3: Check if already fully paid
            if invoice.payment_state == 'paid':
                return request.make_json_response({
                    'error': 'Already Paid',
                    'message': 'This invoice is already fully paid'
                }, status=400)
            
            # Step 4: Get or validate journal
            if journal_id:
                journal = request.env['account.journal'].browse(journal_id)
                if not journal.exists() or journal.type not in ['bank', 'cash']:
                    return request.make_json_response({
                        'error': 'Invalid Journal',
                        'message': 'Journal must be a bank or cash journal'
                    }, status=400)
            else:
                # Find default bank journal
                journal = request.env['account.journal'].search([
                    ('type', '=', 'bank'),
                    ('company_id', '=', invoice.company_id.id)
                ], limit=1)
                
                if not journal:
                    # Try cash journal as fallback
                    journal = request.env['account.journal'].search([
                        ('type', '=', 'cash'),
                        ('company_id', '=', invoice.company_id.id)
                    ], limit=1)
                
                if not journal:
                    return request.make_json_response({
                        'error': 'Configuration Error',
                        'message': 'No bank or cash journal found. Please configure payment journals.'
                    }, status=500)
            
            _logger.info(f"Using journal: {journal.name} (ID: {journal.id})")
            
            # Step 5: Create payment using payment register wizard
            try:
                # Determine if this is a partial payment
                is_partial_payment = float(amount) < invoice.amount_residual
                
                wizard_vals = {
                    'amount': float(amount),
                    'payment_date': payment_date or fields.Date.today(),
                    'journal_id': journal.id,
                }
                
                # Handle partial payments - keep invoice open for remaining amount
                if is_partial_payment:
                    wizard_vals['payment_difference_handling'] = 'open'
                    _logger.info(f"Partial payment detected: {amount} < {invoice.amount_residual}")
                else:
                    wizard_vals['payment_difference_handling'] = 'reconcile'
                    _logger.info(f"Full payment: {amount} >= {invoice.amount_residual}")
                
                payment_wizard = request.env['account.payment.register'].with_context(
                    active_model='account.move',
                    active_ids=invoice.ids,
                    allowed_company_ids=[invoice.company_id.id]
                ).create(wizard_vals)
                
                _logger.info(f"Payment wizard created with amount: {amount}")
                
                # Create and post payment
                payment_result = payment_wizard.action_create_payments()
                
                # Get created payment
                payment = None
                if payment_result and 'res_id' in payment_result:
                    payment = request.env['account.payment'].browse(payment_result['res_id'])
                elif payment_result and 'domain' in payment_result:
                    # Sometimes returns domain instead of res_id
                    payment_ids = request.env['account.payment'].search(payment_result['domain'], limit=1)
                    if payment_ids:
                        payment = payment_ids[0]
                
                if not payment:
                    # Try to find the most recent payment for this invoice
                    payment = request.env['account.payment'].search([
                        ('move_id.line_ids.matched_debit_ids.debit_move_id.move_id', '=', invoice.id)
                    ], order='create_date desc', limit=1)
                    
                    if not payment:
                        payment = request.env['account.payment'].search([
                            ('move_id.line_ids.matched_credit_ids.credit_move_id.move_id', '=', invoice.id)
                        ], order='create_date desc', limit=1)
                
                if payment:
                    # Update payment memo (reference) field
                    payment.write({
                        'memo': payment_reference,
                        'payment_reference': payment_reference
                    })
                    
                    _logger.info(f"Payment created: {payment.name} (ID: {payment.id})")
                    
                    # Refresh invoice to get updated payment state
                    invoice.invalidate_recordset()
                    fee.invalidate_recordset()
                    
                    return request.make_json_response({
                        'status': 'success',
                        'message': 'Payment recorded and reconciled successfully',
                        'data': {
                            'fee_id': fee.id,
                            'fee_display_name': fee.display_name,
                            'invoice_id': invoice.id,
                            'invoice_number': invoice.name,
                            'invoice_state': invoice.state,
                            'payment_id': payment.id,
                            'payment_name': payment.name,
                            'payment_state': payment.state,
                            'amount_paid': float(amount),
                            'invoice_payment_state': invoice.payment_state,
                            'invoice_amount_total': invoice.amount_total,
                            'invoice_amount_residual': invoice.amount_residual,
                            'payment_reference': payment_reference,
                            'payment_date': payment.date.isoformat() if payment.date else None,
                            'journal_name': journal.name
                        }
                    }, status=200)
                else:
                    _logger.warning("Payment created but could not retrieve payment record")
                    return request.make_json_response({
                        'status': 'success',
                        'message': 'Payment created but details unavailable',
                        'data': {
                            'fee_id': fee.id,
                            'invoice_id': invoice.id,
                            'invoice_number': invoice.name,
                            'amount_paid': float(amount),
                            'payment_reference': payment_reference
                        }
                    }, status=200)
                    
            except Exception as e:
                _logger.error(f"Payment creation failed: {str(e)}")
                import traceback
                _logger.error(traceback.format_exc())
                return request.make_json_response({
                    'error': 'Payment Creation Failed',
                    'message': str(e)
                }, status=500)
        
        except Exception as e:
            _logger.error(f"Error in record_payment: {str(e)}")
            import traceback
            _logger.error(traceback.format_exc())
            return request.make_json_response({
                'error': 'Server Error',
                'message': str(e)
            }, status=500)
