from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import timedelta

class SchoolStudentFee(models.Model):
    _name = "school.student.fee"
    _description = "Student Fee Invoice"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "display_name"

    student_id = fields.Many2one("school.student", required=True, tracking=True)

    academic_year_id = fields.Many2one("school.academic.year", required=True, tracking=True)

    term = fields.Selection([
        ("t1", "Term 1"),
        ("t2", "Term 2"),
        ("t3", "Term 3"),
    ], required=True, default="t1", tracking=True)

    structure_id = fields.Many2one("school.fee.structure", required=True)

    invoice_id = fields.Many2one("account.move", readonly=True, copy=False)

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    # Payment tracking fields
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
    ], string='Payment Status', compute='_compute_payment_state', store=True)

    amount_paid = fields.Monetary(
        compute='_compute_payment_amounts',
        store=True,
        currency_field='currency_id',
        string='Amount Paid'
    )

    amount_due = fields.Monetary(
        compute='_compute_payment_amounts',
        store=True,
        currency_field='currency_id',
        string='Amount Due'
    )

    # Discount fields
    discount_type = fields.Selection([
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ], string='Discount Type')

    discount_value = fields.Float(string='Discount Value')

    discount_amount = fields.Monetary(
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id',
        string='Discount Amount'
    )
    
    # Scholarship
    scholarship_id = fields.Many2one(
        'school.scholarship',
        string='Scholarship',
        tracking=True
    )
    
    scholarship_amount = fields.Monetary(
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id',
        string='Scholarship Amount'
    )
    
    # Sibling discount
    has_sibling_discount = fields.Boolean(
        compute='_compute_sibling_discount',
        store=True,
        string='Has Sibling Discount'
    )
    
    sibling_count = fields.Integer(
        compute='_compute_sibling_discount',
        store=True,
        string='Number of Siblings'
    )
    
    sibling_discount_percent = fields.Float(
        compute='_compute_sibling_discount',
        store=True,
        string='Sibling Discount %'
    )
    
    sibling_discount_amount = fields.Monetary(
        compute='_compute_amount_total',
        store=True,
        currency_field='currency_id',
        string='Sibling Discount'
    )
    
    apply_sibling_discount = fields.Boolean(
        string='Apply Sibling Discount',
        default=True,
        help='Automatically apply discount for siblings enrolled in school'
    )

    # Due date and late fees
    due_date = fields.Date(string='Due Date', required=True, tracking=True, 
                           default=lambda self: fields.Date.today())

    is_overdue = fields.Boolean(
        compute='_compute_overdue',
        store=True,
        string='Overdue'
    )

    days_overdue = fields.Integer(
        compute='_compute_overdue',
        store=True,
        string='Days Overdue'
    )
    
    # Late fee configuration
    apply_late_fee = fields.Boolean(
        string='Apply Late Fee',
        default=True,
        help='Automatically apply late fee for overdue payments'
    )
    
    late_fee_amount = fields.Monetary(
        compute='_compute_late_fee',
        store=True,
        currency_field='currency_id',
        string='Late Fee'
    )
    
    late_fee_applied = fields.Boolean(
        string='Late Fee Applied',
        default=False,
        help='Late fee has been added to invoice'
    )

    amount_total = fields.Monetary(
        compute="_compute_amount_total",
        store=True,
        currency_field="currency_id"
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("invoiced", "Invoiced"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
    ], default="draft", tracking=True)

    display_name = fields.Char(compute="_compute_display_name", store=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    _sql_constraints = [
        ("unique_student_term",
         "unique(student_id, academic_year_id, term)",
         "Student already has a fee record for this term and academic year!")
    ]

    @api.depends("student_id.name", "term", "academic_year_id.name")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"{rec.student_id.name} - {rec.academic_year_id.name} - {rec.term}"
    
    @api.depends('student_id', 'student_id.parent_ids', 'apply_sibling_discount', 'academic_year_id')
    def _compute_sibling_discount(self):
        """
        Calculate sibling discount based on number of siblings enrolled.
        Discount rates (configurable via system parameters):
        - 2 siblings: 10%
        - 3 siblings: 15%
        - 4+ siblings: 20%
        """
        for rec in self:
            if not rec.student_id or not rec.apply_sibling_discount or not rec.student_id.parent_ids:
                rec.has_sibling_discount = False
                rec.sibling_count = 0
                rec.sibling_discount_percent = 0.0
                continue
            
            # Find siblings: students who share at least one parent
            parent_ids = rec.student_id.parent_ids.ids
            
            # Search for other students with same parents in the same academic year
            siblings = self.env['school.student'].search([
                ('parent_ids', 'in', parent_ids),
                ('id', '!=', rec.student_id.id),
                ('status', 'in', ['enrolled', 'active']),
                ('academic_year_id', '=', rec.academic_year_id.id),
            ])
            
            sibling_count = len(siblings)
            rec.sibling_count = sibling_count
            
            if sibling_count > 0:
                rec.has_sibling_discount = True
                
                # Get discount rates from system parameters
                IrConfigParam = self.env['ir.config_parameter'].sudo()
                discount_2_siblings = float(IrConfigParam.get_param(
                    'school_fees.sibling_discount_2', default='10.0'
                ))
                discount_3_siblings = float(IrConfigParam.get_param(
                    'school_fees.sibling_discount_3', default='15.0'
                ))
                discount_4_plus_siblings = float(IrConfigParam.get_param(
                    'school_fees.sibling_discount_4_plus', default='20.0'
                ))
                
                # Calculate discount percentage based on sibling count
                if sibling_count == 1:
                    rec.sibling_discount_percent = discount_2_siblings
                elif sibling_count == 2:
                    rec.sibling_discount_percent = discount_3_siblings
                else:  # 3 or more siblings
                    rec.sibling_discount_percent = discount_4_plus_siblings
            else:
                rec.has_sibling_discount = False
                rec.sibling_discount_percent = 0.0

    @api.depends("structure_id.total_amount", "discount_type", "discount_value", "scholarship_id", "sibling_discount_percent")
    def _compute_amount_total(self):
        for rec in self:
            base_amount = rec.structure_id.total_amount
            discount = 0.0
            scholarship = 0.0
            sibling_discount = 0.0
            
            # Apply manual discount
            if rec.discount_type == 'percent' and rec.discount_value:
                discount = base_amount * (rec.discount_value / 100)
            elif rec.discount_type == 'fixed' and rec.discount_value:
                discount = rec.discount_value
            
            # Apply scholarship
            if rec.scholarship_id:
                scholarship = rec.scholarship_id.calculate_discount(base_amount)
            
            # Apply sibling discount
            if rec.has_sibling_discount and rec.sibling_discount_percent > 0:
                sibling_discount = base_amount * (rec.sibling_discount_percent / 100)
            
            rec.discount_amount = discount
            rec.scholarship_amount = scholarship
            rec.sibling_discount_amount = sibling_discount
            rec.amount_total = base_amount - discount - scholarship - sibling_discount

    @api.depends('invoice_id.payment_state', 'invoice_id.amount_residual')
    def _compute_payment_state(self):
        for rec in self:
            if rec.invoice_id:
                rec.payment_state = rec.invoice_id.payment_state
                # Auto-update state based on payment
                if rec.invoice_id.payment_state == 'paid' and rec.state == 'invoiced':
                    rec.state = 'paid'
            else:
                rec.payment_state = 'not_paid'

    @api.depends('invoice_id.amount_total', 'invoice_id.amount_residual')
    def _compute_payment_amounts(self):
        for rec in self:
            if rec.invoice_id:
                rec.amount_paid = rec.invoice_id.amount_total - rec.invoice_id.amount_residual
                rec.amount_due = rec.invoice_id.amount_residual
            else:
                rec.amount_paid = 0.0
                rec.amount_due = rec.amount_total

    @api.depends('due_date', 'payment_state')
    def _compute_overdue(self):
        today = fields.Date.today()
        for rec in self:
            if rec.payment_state not in ['paid', 'reversed'] and rec.due_date:
                if rec.due_date < today:
                    rec.is_overdue = True
                    rec.days_overdue = (today - rec.due_date).days
                else:
                    rec.is_overdue = False
                    rec.days_overdue = 0
            else:
                rec.is_overdue = False
                rec.days_overdue = 0
    
    @api.depends('days_overdue', 'amount_total', 'apply_late_fee')
    def _compute_late_fee(self):
        """
        Calculate late fee based on days overdue.
        Default: 1% per week, max 10%
        Can be customized via system parameters.
        """
        for rec in self:
            if rec.is_overdue and rec.apply_late_fee and rec.days_overdue > 0:
                # Get late fee configuration from system parameters
                IrConfigParam = self.env['ir.config_parameter'].sudo()
                late_fee_percent_per_week = float(IrConfigParam.get_param(
                    'school_fees.late_fee_percent_per_week', default='1.0'
                ))
                late_fee_max_percent = float(IrConfigParam.get_param(
                    'school_fees.late_fee_max_percent', default='10.0'
                ))
                
                weeks_overdue = rec.days_overdue / 7
                late_fee_percent = min(weeks_overdue * late_fee_percent_per_week, late_fee_max_percent)
                rec.late_fee_amount = rec.amount_total * (late_fee_percent / 100)
            else:
                rec.late_fee_amount = 0.0

    def action_generate_invoice(self):
        for rec in self:
            if rec.invoice_id:
                raise ValidationError("Invoice already generated!")

            # Get or create partner for billing
            partner = rec.student_id.partner_id
            if not partner:
                # Try to get first parent's partner
                if rec.student_id.parent_ids and rec.student_id.parent_ids[0].partner_id:
                    partner = rec.student_id.parent_ids[0].partner_id
                else:
                    # Create a partner for the student
                    partner = self.env['res.partner'].create({
                        'name': rec.student_id.name,
                        'email': rec.student_id.email,
                        'phone': rec.student_id.phone,
                        'is_company': False,
                    })
                    rec.student_id.partner_id = partner.id

            invoice_lines = []
            
            # Add fee structure lines
            for line in rec.structure_id.line_ids:
                invoice_lines.append((0, 0, {
                    "product_id": line.product_id.id,
                    "name": line.product_id.name,
                    "quantity": 1,
                    "price_unit": line.amount,
                }))
            
            # Apply manual discount if exists
            if rec.discount_amount > 0:
                discount_product = self.env.ref(
                    'school_fees.product_discount',
                    raise_if_not_found=False
                )
                if discount_product:
                    discount_name = f"Discount ({rec.discount_type}: {rec.discount_value})"
                    invoice_lines.append((0, 0, {
                        "product_id": discount_product.id,
                        "name": discount_name,
                        "quantity": 1,
                        "price_unit": -rec.discount_amount,  # Negative for discount
                    }))
            
            # Apply scholarship discount if exists
            if rec.scholarship_amount > 0:
                scholarship_product = self.env.ref(
                    'school_fees.product_scholarship',
                    raise_if_not_found=False
                )
                if scholarship_product:
                    scholarship_name = f"Scholarship: {rec.scholarship_id.name}"
                    invoice_lines.append((0, 0, {
                        "product_id": scholarship_product.id,
                        "name": scholarship_name,
                        "quantity": 1,
                        "price_unit": -rec.scholarship_amount,  # Negative for discount
                    }))
            
            # Apply sibling discount if exists
            if rec.sibling_discount_amount > 0:
                sibling_product = self.env.ref(
                    'school_fees.product_sibling_discount',
                    raise_if_not_found=False
                )
                if sibling_product:
                    sibling_name = f"Sibling Discount ({rec.sibling_count + 1} siblings - {rec.sibling_discount_percent}%)"
                    invoice_lines.append((0, 0, {
                        "product_id": sibling_product.id,
                        "name": sibling_name,
                        "quantity": 1,
                        "price_unit": -rec.sibling_discount_amount,  # Negative for discount
                    }))

            move = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": partner.id,
                "invoice_date": fields.Date.today(),
                "invoice_line_ids": invoice_lines,
            })

            rec.invoice_id = move.id
            rec.state = "invoiced"

    def action_view_invoice(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Invoice",
            "res_model": "account.move",
            "view_mode": "form",
            "res_id": self.invoice_id.id,
            "target": "current",
        }

    def action_update_payment_status(self):
        for rec in self:
            if rec.invoice_id and rec.invoice_id.payment_state == "paid":
                rec.state = "paid"
    
    def action_apply_late_fee(self):
        """Manually apply late fee to invoice"""
        for rec in self:
            if not rec.invoice_id:
                raise ValidationError("No invoice to apply late fee to!")
            
            if rec.late_fee_applied:
                raise ValidationError("Late fee already applied!")
            
            if rec.late_fee_amount <= 0:
                raise ValidationError("No late fee to apply!")
            
            # Get late fee product
            late_fee_product = self.env.ref(
                'school_fees.product_late_fee',
                raise_if_not_found=False
            )
            
            if not late_fee_product:
                raise ValidationError(
                    "Late fee product not found! Please configure it in settings."
                )
            
            # Add late fee line to invoice
            self.env['account.move.line'].create({
                'move_id': rec.invoice_id.id,
                'product_id': late_fee_product.id,
                'name': f'Late Fee ({rec.days_overdue} days overdue)',
                'quantity': 1,
                'price_unit': rec.late_fee_amount,
            })
            
            rec.late_fee_applied = True
            
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Late Fee Applied',
                    'message': f'Late fee of {rec.late_fee_amount} applied to invoice.',
                    'type': 'success',
                    'sticky': False,
                }
            }
    
    def cron_apply_late_fees(self):
        """
        Scheduled action to automatically apply late fees to overdue invoices.
        Run daily.
        """
        overdue_fees = self.search([
            ('is_overdue', '=', True),
            ('apply_late_fee', '=', True),
            ('late_fee_applied', '=', False),
            ('late_fee_amount', '>', 0),
            ('invoice_id', '!=', False),
            ('payment_state', '!=', 'paid'),
        ])
        
        applied_count = 0
        for fee in overdue_fees:
            try:
                fee.action_apply_late_fee()
                applied_count += 1
            except Exception as e:
                # Log error but continue with other fees
                fee.message_post(
                    body=f"Failed to apply late fee: {str(e)}",
                    message_type='notification'
                )
        
        return applied_count
    
    def cron_send_payment_reminders(self):
        """
        Scheduled action to send payment reminder emails.
        Run daily.
        """
        # Find fees due in 7 days (first reminder)
        date_7_days = fields.Date.today() + timedelta(days=7)
        fees_due_soon = self.search([
            ('due_date', '=', date_7_days),
            ('payment_state', '!=', 'paid'),
            ('state', '=', 'invoiced'),
        ])
        
        # Find overdue fees (second reminder)
        fees_overdue = self.search([
            ('is_overdue', '=', True),
            ('payment_state', '!=', 'paid'),
            ('state', '=', 'invoiced'),
        ])
        
        template_reminder = self.env.ref(
            'school_fees.email_template_payment_reminder',
            raise_if_not_found=False
        )
        template_overdue = self.env.ref(
            'school_fees.email_template_payment_overdue',
            raise_if_not_found=False
        )
        
        sent_count = 0
        
        # Send reminders for fees due soon
        if template_reminder:
            for fee in fees_due_soon:
                # Check if student has parents with email or student has email
                has_email = False
                if fee.student_id.parent_ids:
                    has_email = any(fee.student_id.parent_ids.mapped('email'))
                elif fee.student_id.email:
                    has_email = True
                
                if has_email:
                    template_reminder.send_mail(fee.id, force_send=True)
                    sent_count += 1
        
        # Send reminders for overdue fees
        if template_overdue:
            for fee in fees_overdue:
                # Check if student has parents with email or student has email
                has_email = False
                if fee.student_id.parent_ids:
                    has_email = any(fee.student_id.parent_ids.mapped('email'))
                elif fee.student_id.email:
                    has_email = True
                
                if has_email:
                    template_overdue.send_mail(fee.id, force_send=True)
                    sent_count += 1
        
        return sent_count
