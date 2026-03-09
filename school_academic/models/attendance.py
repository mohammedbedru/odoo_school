from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolAttendance(models.Model):
    _name = "school.attendance"
    _description = "Student Attendance"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"
    _sql_constraints = [
        ("unique_attendance", "unique(date, section_id)",
         "Attendance already exists for this section on this date!")
    ]

    name = fields.Char(compute="_compute_name", store=True)

    date = fields.Date(required=True, default=fields.Date.today, tracking=True)
    section_id = fields.Many2one("school.section", required=True, tracking=True)

    teacher_id = fields.Many2one("school.teacher", tracking=True)

    line_ids = fields.One2many("school.attendance.line", "attendance_id", string="Attendance Lines")

    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
    ], default="draft", tracking=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    @api.depends("date", "section_id.full_name")
    def _compute_name(self):
        for rec in self:
            if rec.section_id and rec.date:
                rec.name = f"Attendance {rec.section_id.full_name} - {rec.date}"
            else:
                rec.name = "Attendance"

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError("Cannot confirm attendance without student lines.")
        self.write({"state": "confirmed"})

    def action_set_draft(self):
        self.write({"state": "draft"})


class SchoolAttendanceLine(models.Model):
    _name = "school.attendance.line"
    _description = "Attendance Line"
    _order = "student_id"

    attendance_id = fields.Many2one("school.attendance", required=True, ondelete="cascade")
    student_id = fields.Many2one("school.student", required=True)

    status = fields.Selection([
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ], default="present", required=True)

    note = fields.Char()

    @api.constrains("student_id", "attendance_id")
    def _check_duplicate_student(self):
        for rec in self:
            domain = [
                ("id", "!=", rec.id),
                ("attendance_id", "=", rec.attendance_id.id),
                ("student_id", "=", rec.student_id.id),
            ]
            if self.search_count(domain):
                raise ValidationError("This student is already in the attendance list.")
