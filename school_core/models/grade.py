from odoo import models, fields

class SchoolGrade(models.Model):
    _name = "school.grade"
    _description = "School Grade"
    _order = "sequence, id"

    name = fields.Char(required=True)
    code = fields.Char()
    sequence = fields.Integer(default=1)

    section_ids = fields.One2many("school.section", "grade_id", string="Sections")
