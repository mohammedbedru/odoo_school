from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolScholarship(models.Model):
    _name = "school.scholarship"
    _description = "Student Scholarship"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(required=True, tracking=True)
    
    scholarship_type = fields.Selection([
        ('merit', 'Merit Based'),
        ('need', 'Need Based'),
        ('sports', 'Sports'),
        ('sibling', 'Sibling Discount'),
        ('staff', 'Staff Child'),
        ('other', 'Other'),
    ], required=True, default='merit', tracking=True)
    
    discount_type = fields.Selection([
        ('percent', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ], required=True, default='percent', tracking=True)
    
    discount_value = fields.Float(required=True, tracking=True)
    
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )
    
    max_amount = fields.Monetary(
        string="Maximum Amount",
        help="Maximum discount amount (for percentage type)",
        currency_field='currency_id'
    )
    
    description = fields.Text()
    
    active = fields.Boolean(default=True)
    
    # Eligibility criteria
    min_grade_percentage = fields.Float(string="Minimum Grade %")
    applicable_grades = fields.Many2many(
        'school.grade',
        string='Applicable Grades',
        help="Leave empty for all grades"
    )
    
    # Statistics
    student_count = fields.Integer(
        compute='_compute_student_count',
        string='Students'
    )
    
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Scholarship code must be unique!')
    ]
    
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = self.env['school.student.fee'].search_count([
                ('scholarship_id', '=', rec.id)
            ])
    
    def action_view_students(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students with Scholarship',
            'res_model': 'school.student.fee',
            'view_mode': 'list,form',
            'domain': [('scholarship_id', '=', self.id)],
            'context': {'default_scholarship_id': self.id}
        }
    
    def calculate_discount(self, base_amount):
        """Calculate discount amount for given base amount"""
        self.ensure_one()
        
        if self.discount_type == 'percent':
            discount = base_amount * (self.discount_value / 100)
            if self.max_amount and discount > self.max_amount:
                discount = self.max_amount
        else:
            discount = self.discount_value
        
        return discount
