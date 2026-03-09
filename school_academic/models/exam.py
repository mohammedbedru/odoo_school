from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolExam(models.Model):
    _name = "school.exam"
    _description = "School Exam"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    name = fields.Char(required=True, tracking=True)

    exam_type = fields.Selection([
        ("quiz", "Quiz"),
        ("mid", "Midterm"),
        ("final", "Final"),
        ("assignment", "Assignment"),
    ], required=True, tracking=True)

    term = fields.Selection([
        ("t1", "Term 1"),
        ("t2", "Term 2"),
        ("t3", "Term 3"),
    ], required=True, tracking=True)

    academic_year_id = fields.Many2one("school.academic.year", tracking=True)

    section_id = fields.Many2one("school.section", required=True, tracking=True)
    subject_id = fields.Many2one("school.subject", required=True, tracking=True)

    teacher_id = fields.Many2one("school.teacher", tracking=True)

    date = fields.Date(required=True, tracking=True)
    max_mark = fields.Float(default=100.0, tracking=True)

    mark_line_ids = fields.One2many("school.exam.mark", "exam_id", string="Marks")

    state = fields.Selection([
        ("draft", "Draft"),
        ("open", "Marks Entry"),
        ("done", "Published"),
    ], default="draft", tracking=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    def action_open(self):
        self.write({"state": "open"})

    def action_publish(self):
        for rec in self:
            if not rec.mark_line_ids:
                raise ValidationError("Cannot publish exam without marks.")
        self.write({"state": "done"})

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_generate_students(self):
        """
        Populate mark lines for all students in section.
        """
        for rec in self:
            students = self.env["school.student"].search([
                ("section_id", "=", rec.section_id.id),
                ("status", "in", ["enrolled", "active"]),
            ])

            existing_students = rec.mark_line_ids.mapped("student_id")
            new_students = students - existing_students

            lines = []
            for st in new_students:
                lines.append((0, 0, {"student_id": st.id}))

            if lines:
                rec.write({"mark_line_ids": lines})


class SchoolExamMark(models.Model):
    _name = "school.exam.mark"
    _description = "Exam Mark"
    _order = "student_id"

    exam_id = fields.Many2one("school.exam", required=True, ondelete="cascade")
    student_id = fields.Many2one("school.student", required=True)

    mark = fields.Float()
    grade = fields.Char(compute="_compute_grade", store=True)
    remark = fields.Char()

    @api.depends("mark", "exam_id.max_mark")
    def _compute_grade(self):
        """
        Simple grading logic.
        You can later move this to a config table.
        """
        for rec in self:
            if rec.mark is None:
                rec.grade = ""
                continue

            percent = 0.0
            if rec.exam_id.max_mark:
                percent = (rec.mark / rec.exam_id.max_mark) * 100

            if percent >= 90:
                rec.grade = "A"
            elif percent >= 75:
                rec.grade = "B"
            elif percent >= 60:
                rec.grade = "C"
            elif percent >= 50:
                rec.grade = "D"
            else:
                rec.grade = "F"

    @api.constrains("mark", "exam_id")
    def _check_mark_range(self):
        for rec in self:
            if rec.mark and rec.exam_id.max_mark and rec.mark > rec.exam_id.max_mark:
                raise ValidationError("Mark cannot exceed maximum mark.")

    @api.constrains("student_id", "exam_id")
    def _check_duplicate_student(self):
        for rec in self:
            domain = [
                ("id", "!=", rec.id),
                ("exam_id", "=", rec.exam_id.id),
                ("student_id", "=", rec.student_id.id),
            ]
            if self.search_count(domain):
                raise ValidationError("This student already has a mark line for this exam.")

