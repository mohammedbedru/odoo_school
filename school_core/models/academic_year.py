from odoo import models, fields

class SchoolAcademicYear(models.Model):
    _name = "school.academic.year"
    _description = "Academic Year"
    _rec_name = "name"

    name = fields.Char(required=True)  # e.g 2025/2026
    date_start = fields.Date(required=True)
    date_end = fields.Date(required=True)
    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )
    _sql_constraints = [
        ('name_unique', 'unique(name)', 'The academic year name must be unique.'),
        ('date_check', 'CHECK (date_start < date_end)', 'The start date must be before the end date.'),
    ]

