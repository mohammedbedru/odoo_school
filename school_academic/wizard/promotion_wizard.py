from odoo import models, fields
from odoo.exceptions import ValidationError


class StudentPromotionWizard(models.TransientModel):
    _name = "school.promotion.wizard"
    _description = "Student Promotion Wizard"

    from_section_id = fields.Many2one("school.section", required=True)
    to_section_id = fields.Many2one("school.section", required=True)

    student_ids = fields.Many2many("school.student", string="Students")

    def action_load_students(self):
        self.ensure_one()
        students = self.env["school.student"].search([
            ("section_id", "=", self.from_section_id.id),
            ("status", "in", ["enrolled", "active"]),
        ])
        self.student_ids = students

        return {
            "type": "ir.actions.act_window",
            "res_model": "school.promotion.wizard",
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_promote(self):
        self.ensure_one()

        if self.from_section_id == self.to_section_id:
            raise ValidationError("From section and To section cannot be the same.")

        if not self.student_ids:
            raise ValidationError("Please select at least one student.")

        self.student_ids.write({
            "section_id": self.to_section_id.id,
            "grade_id": self.to_section_id.grade_id.id,
        })

        return {"type": "ir.actions.act_window_close"}
