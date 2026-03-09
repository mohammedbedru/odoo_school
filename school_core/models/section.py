from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SchoolSection(models.Model):
    _name = "school.section"
    _description = "School Section"
    _rec_name = "full_name"

    name = fields.Char(required=True)  # A, B, C
    grade_id = fields.Many2one("school.grade", required=True)
    full_name = fields.Char(compute="_compute_full_name", store=True)

    capacity = fields.Integer(default=40)
    class_teacher_id = fields.Many2one("school.teacher")

    student_ids = fields.One2many("school.student", "section_id")
    student_count = fields.Integer(compute="_compute_student_count", store=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    @api.depends("name", "grade_id.name")
    def _compute_full_name(self):
        for rec in self:
            rec.full_name = f"{rec.grade_id.name}-{rec.name}" if rec.grade_id else rec.name

    @api.depends("student_ids")
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)
    
    @api.constrains("capacity", "student_ids")
    def _check_capacity(self):
        for rec in self:
            if rec.capacity and len(rec.student_ids) > rec.capacity:
                raise ValidationError("Section capacity exceeded!")
