from odoo import models, fields, api

class SchoolSubjectAssignment(models.Model):
    _name = "school.subject.assignment"
    _description = "Subject Assignment"
    _rec_name = "display_name"
    _sql_constraints = [
        ("unique_subject_section", "unique(section_id, subject_id)",
         "This subject is already assigned to this section!")
    ]

    section_id = fields.Many2one("school.section", required=True)
    subject_id = fields.Many2one("school.subject", required=True)
    teacher_id = fields.Many2one("school.teacher", required=True)

    hours_per_week = fields.Float(default=1.0)
    display_name = fields.Char(compute="_compute_display_name", store=True)
    section_grade_id = fields.Many2one('school.grade', related='section_id.grade_id', store=False)

    @api.depends("section_id", "section_id.full_name", "subject_id", "subject_id.name")
    def _compute_display_name(self):
        for rec in self:
            if rec.section_id and rec.subject_id:
                # Ensure we handle cases where names might be empty
                section_name = rec.section_id.full_name or "New Section"
                subject_name = rec.subject_id.name or "New Subject"
                rec.display_name = f"{section_name} - {subject_name}"
            else:
                rec.display_name = "New Assignment"
                
    @api.onchange('section_id')
    def _onchange_section_id(self):
        if self.section_id:
            return {'domain': {'subject_id': [('grade_id', '=', self.section_id.grade_id.id)]}}
        else:
            return {'domain': {'subject_id': []}}