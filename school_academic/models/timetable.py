from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolTimetable(models.Model):
    _name = "school.timetable"
    _description = "School Timetable"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date_start desc, id desc"

    name = fields.Char(required=True, tracking=True)
    section_id = fields.Many2one("school.section", required=True, tracking=True)

    date_start = fields.Date(required=True, tracking=True)
    date_end = fields.Date(required=True, tracking=True)

    line_ids = fields.One2many("school.timetable.line", "timetable_id", string="Lines")

    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
    ], default="draft", tracking=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    def action_confirm(self):
        self.write({"state": "confirmed"})

    def action_set_draft(self):
        self.write({"state": "draft"})

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start and rec.date_end and rec.date_end < rec.date_start:
                raise ValidationError("End date cannot be before start date.")


class SchoolTimetableLine(models.Model):
    _name = "school.timetable.line"
    _description = "Timetable Line"
    _order = "day_of_week, period"

    timetable_id = fields.Many2one("school.timetable", required=True, ondelete="cascade")
    section_id = fields.Many2one(related="timetable_id.section_id", store=True)

    day_of_week = fields.Selection([
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
        ("6", "Sunday"),
    ], required=True)

    period = fields.Integer(required=True)  # 1,2,3...
    subject_id = fields.Many2one("school.subject", required=True)
    teacher_id = fields.Many2one("school.teacher", required=True)

    room = fields.Char()

    start_time = fields.Float(help="Hour in 24 format, e.g 8.5 for 08:30")
    end_time = fields.Float(help="Hour in 24 format, e.g 10.0 for 10:00")

    @api.constrains("start_time", "end_time")
    def _check_time(self):
        for rec in self:
            if rec.start_time and rec.end_time and rec.end_time <= rec.start_time:
                raise ValidationError("End time must be greater than start time.")

    @api.constrains("day_of_week", "period", "teacher_id", "timetable_id")
    def _check_teacher_conflict(self):
        """
        Prevent same teacher assigned twice in same day+period in same timetable.
        (Simple conflict detection)
        """
        for rec in self:
            if not rec.teacher_id:
                continue

            domain = [
                ("id", "!=", rec.id),
                ("timetable_id", "=", rec.timetable_id.id),
                ("day_of_week", "=", rec.day_of_week),
                ("period", "=", rec.period),
                ("teacher_id", "=", rec.teacher_id.id),
            ]
            if self.search_count(domain):
                raise ValidationError("Teacher conflict: this teacher is already assigned in same day and period.")
