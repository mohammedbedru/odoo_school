from odoo import models, fields, api


class SchoolStudent(models.Model):
    _inherit = "school.student"
    
    # Fee balance fields
    total_fees = fields.Monetary(
        compute='_compute_fee_balance',
        string='Total Fees',
        currency_field='currency_id'
    )
    
    total_paid = fields.Monetary(
        compute='_compute_fee_balance',
        string='Total Paid',
        currency_field='currency_id'
    )
    
    total_due = fields.Monetary(
        compute='_compute_fee_balance',
        string='Total Due',
        currency_field='currency_id'
    )
    
    fee_count = fields.Integer(
        compute='_compute_fee_balance',
        string='Fee Records'
    )
    
    has_overdue_fees = fields.Boolean(
        compute='_compute_fee_balance',
        string='Has Overdue Fees'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    @api.depends('name')  # Dummy dependency to trigger recompute
    def _compute_fee_balance(self):
        for student in self:
            fees = self.env['school.student.fee'].search([
                ('student_id', '=', student.id)
            ])
            
            student.fee_count = len(fees)
            student.total_fees = sum(fees.mapped('amount_total'))
            student.total_paid = sum(fees.mapped('amount_paid'))
            student.total_due = sum(fees.mapped('amount_due'))
            student.has_overdue_fees = any(fees.mapped('is_overdue'))
    
    def action_view_fees(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Fees',
            'res_model': 'school.student.fee',
            'view_mode': 'list,form',
            'domain': [('student_id', '=', self.id)],
            'context': {'default_student_id': self.id}
        }
