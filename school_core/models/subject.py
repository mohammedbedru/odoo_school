from odoo import models, fields

class SchoolSubject(models.Model):
    _name = "school.subject"
    _description = "School Subject"

    name = fields.Char(required=True)
    code = fields.Char()
    credit = fields.Float(default=1.0)

    grade_id = fields.Many2one("school.grade")
