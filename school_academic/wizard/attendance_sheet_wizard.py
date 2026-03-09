from odoo import models, fields
from odoo.exceptions import ValidationError


class AttendanceSheetWizard(models.TransientModel):
    _name = "school.attendance.sheet.wizard"
    _description = "Attendance Sheet Wizard"

    date = fields.Date(required=True, default=fields.Date.today)
    section_id = fields.Many2one("school.section", required=True)
    teacher_id = fields.Many2one("school.teacher")

    def action_generate_attendance(self):
        self.ensure_one()

        existing = self.env["school.attendance"].search([
            ("date", "=", self.date),
            ("section_id", "=", self.section_id.id),
        ], limit=1)

        if existing:
            raise ValidationError("Attendance already exists for this section and date.")

        students = self.env["school.student"].search([
            ("section_id", "=", self.section_id.id),
            ("status", "in", ["enrolled", "active"]),
        ])

        if not students:
            raise ValidationError("No active students found in this section.")

        lines = []
        for st in students:
            lines.append((0, 0, {
                "student_id": st.id,
                "status": "present",
            }))

        attendance = self.env["school.attendance"].create({
            "date": self.date,
            "section_id": self.section_id.id,
            "teacher_id": self.teacher_id.id if self.teacher_id else False,
            "line_ids": lines,
        })

        return {
            "type": "ir.actions.act_window",
            "name": "Attendance",
            "res_model": "school.attendance",
            "res_id": attendance.id,
            "view_mode": "form",
            "target": "current",
        }
