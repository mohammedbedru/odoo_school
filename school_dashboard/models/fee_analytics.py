from odoo import models, fields, api
from datetime import datetime, timedelta

class FeeAnalytics(models.Model):
    _name = "school.fee.analytics"
    _description = "Fee Collection Analytics"
    _auto = False
    _rec_name = "academic_year_id"
    
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', readonly=True)
    term = fields.Selection([
        ('t1', 'Term 1'),
        ('t2', 'Term 2'),
        ('t3', 'Term 3'),
    ], string='Term', readonly=True)
    grade_id = fields.Many2one('school.grade', string='Grade', readonly=True)
    
    total_amount = fields.Monetary(string='Total Amount', readonly=True, currency_field='currency_id')
    collected_amount = fields.Monetary(string='Collected Amount', readonly=True, currency_field='currency_id')
    pending_amount = fields.Monetary(string='Pending Amount', readonly=True, currency_field='currency_id')
    overdue_amount = fields.Monetary(string='Overdue Amount', readonly=True, currency_field='currency_id')
    
    student_count = fields.Integer(string='Students', readonly=True)
    paid_count = fields.Integer(string='Paid Students', readonly=True)
    pending_count = fields.Integer(string='Pending Students', readonly=True)
    overdue_count = fields.Integer(string='Overdue Students', readonly=True)
    
    collection_rate = fields.Float(string='Collection Rate %', readonly=True)
    
    currency_id = fields.Many2one('res.currency', readonly=True)
    
    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW school_fee_analytics AS (
                SELECT
                    ROW_NUMBER() OVER() as id,
                    sf.academic_year_id,
                    sf.term,
                    s.grade_id,
                    sf.currency_id,
                    COUNT(DISTINCT sf.student_id) as student_count,
                    SUM(sf.amount_total + sf.amount_paid) as total_amount,
                    SUM(sf.amount_paid) as collected_amount,
                    SUM(sf.amount_due) as pending_amount,
                    SUM(CASE WHEN sf.is_overdue = true THEN sf.amount_due ELSE 0 END) as overdue_amount,
                    SUM(CASE WHEN sf.payment_state = 'paid' THEN 1 ELSE 0 END) as paid_count,
                    SUM(CASE WHEN sf.payment_state != 'paid' THEN 1 ELSE 0 END) as pending_count,
                    SUM(CASE WHEN sf.is_overdue = true THEN 1 ELSE 0 END) as overdue_count,
                    CASE 
                        WHEN SUM(sf.amount_total + sf.amount_paid) > 0 
                        THEN (SUM(sf.amount_paid) / SUM(sf.amount_total + sf.amount_paid) * 100)
                        ELSE 0 
                    END as collection_rate
                FROM school_student_fee sf
                JOIN school_student s ON s.id = sf.student_id
                GROUP BY sf.academic_year_id, sf.term, s.grade_id, sf.currency_id
            )
        """)


class MonthlyFeeCollection(models.Model):
    _name = "school.monthly.fee.collection"
    _description = "Monthly Fee Collection Report"
    
    name = fields.Char(compute='_compute_name', store=True)
    month = fields.Selection([
        ('01', 'January'), ('02', 'February'), ('03', 'March'),
        ('04', 'April'), ('05', 'May'), ('06', 'June'),
        ('07', 'July'), ('08', 'August'), ('09', 'September'),
        ('10', 'October'), ('11', 'November'), ('12', 'December'),
    ], string='Month', required=True)
    year = fields.Char(string='Year', required=True, default=lambda self: str(datetime.now().year))
    
    total_collected = fields.Monetary(compute='_compute_collection', string='Total Collected', store=True, currency_field='currency_id')
    total_invoices = fields.Integer(compute='_compute_collection', string='Total Invoices', store=True)
    paid_invoices = fields.Integer(compute='_compute_collection', string='Paid Invoices', store=True)
    pending_invoices = fields.Integer(compute='_compute_collection', string='Pending Invoices', store=True)
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    @api.depends('month', 'year')
    def _compute_name(self):
        for rec in self:
            month_name = dict(rec._fields['month'].selection).get(rec.month, '')
            rec.name = f"{month_name} {rec.year}"
    
    @api.depends('month', 'year')
    def _compute_collection(self):
        for rec in self:
            # Get first and last day of month
            year = int(rec.year)
            month = int(rec.month)
            first_day = datetime(year, month, 1).date()
            
            if month == 12:
                last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            # Get invoices for this month
            invoices = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', first_day),
                ('invoice_date', '<=', last_day),
            ])
            
            rec.total_invoices = len(invoices)
            rec.paid_invoices = len(invoices.filtered(lambda inv: inv.payment_state == 'paid'))
            rec.pending_invoices = len(invoices.filtered(lambda inv: inv.payment_state != 'paid'))
            
            # Calculate total collected
            paid_invoices = invoices.filtered(lambda inv: inv.payment_state == 'paid')
            rec.total_collected = sum(paid_invoices.mapped('amount_total'))


class FeeDefaulterReport(models.Model):
    _name = "school.fee.defaulter"
    _description = "Fee Defaulter Report"
    _order = "days_overdue desc"
    
    student_id = fields.Many2one('school.student', string='Student', required=True)
    grade_id = fields.Many2one('school.grade', related='student_id.grade_id', string='Grade', store=True)
    section_id = fields.Many2one('school.section', related='student_id.section_id', string='Section', store=True)
    
    total_due = fields.Monetary(compute='_compute_due_amount', string='Total Due', store=True, currency_field='currency_id')
    overdue_fees = fields.Integer(compute='_compute_due_amount', string='Overdue Fees', store=True)
    days_overdue = fields.Integer(compute='_compute_due_amount', string='Days Overdue', store=True)
    last_payment_date = fields.Date(compute='_compute_due_amount', string='Last Payment', store=True)
    
    contact_phone = fields.Char(compute='_compute_contact_info', string='Phone', store=True)
    contact_email = fields.Char(compute='_compute_contact_info', string='Email', store=True)
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    @api.depends('student_id', 'student_id.parent_ids', 'student_id.email', 'student_id.phone')
    def _compute_contact_info(self):
        """Get contact info from parents or student"""
        for rec in self:
            if rec.student_id.parent_ids:
                # Get first parent's contact info
                first_parent = rec.student_id.parent_ids[0]
                rec.contact_phone = first_parent.phone or first_parent.mobile
                rec.contact_email = first_parent.email
            else:
                # Fallback to student's contact info
                rec.contact_phone = rec.student_id.phone
                rec.contact_email = rec.student_id.email
    
    @api.depends('student_id')
    def _compute_due_amount(self):
        for rec in self:
            fees = self.env['school.student.fee'].search([
                ('student_id', '=', rec.student_id.id),
                ('is_overdue', '=', True)
            ])
            
            rec.total_due = sum(fees.mapped('amount_due'))
            rec.overdue_fees = len(fees)
            rec.days_overdue = max(fees.mapped('days_overdue')) if fees else 0
            
            # Get last payment date from student's invoices
            partner = rec.student_id.partner_id
            if not partner and rec.student_id.parent_ids:
                partner = rec.student_id.parent_ids[0].partner_id
            
            if partner:
                paid_invoices = self.env['account.move'].search([
                    ('partner_id', '=', partner.id),
                    ('payment_state', '=', 'paid'),
                    ('move_type', '=', 'out_invoice')
                ], order='invoice_date desc', limit=1)
                
                rec.last_payment_date = paid_invoices.invoice_date if paid_invoices else False
            else:
                rec.last_payment_date = False
    
    def action_send_reminder(self):
        self.ensure_one()
        template = self.env.ref('school_fees.email_template_payment_overdue', raise_if_not_found=False)
        
        # Check if student has parents with email or student has email
        has_email = False
        if self.student_id.parent_ids:
            has_email = any(self.student_id.parent_ids.mapped('email'))
        elif self.student_id.email:
            has_email = True
        
        if template and has_email:
            fees = self.env['school.student.fee'].search([
                ('student_id', '=', self.student_id.id),
                ('is_overdue', '=', True)
            ], limit=1)
            if fees:
                template.send_mail(fees.id, force_send=True)
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Reminder Sent',
                'message': f'Payment reminder sent to {self.student_id.name}',
                'type': 'success',
                'sticky': False,
            }
        }
