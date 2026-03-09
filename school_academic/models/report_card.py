from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SchoolReportCard(models.Model):
    _name = "school.report.card"
    _description = "Student Report Card"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "academic_year_id desc, term, student_id"

    name = fields.Char(compute="_compute_name", store=True)

    student_id = fields.Many2one("school.student", required=True, tracking=True)
    section_id = fields.Many2one("school.section", store=True)

    @api.onchange("student_id")
    def _onchange_student_id(self):
        if self.student_id:
            self.section_id = self.student_id.section_id
        else:
            self.section_id = False

    term = fields.Selection([
        ("t1", "Term 1"),
        ("t2", "Term 2"),
        ("t3", "Term 3"),
    ], required=True, tracking=True)

    academic_year_id = fields.Many2one("school.academic.year", required=True, tracking=True)

    line_ids = fields.One2many("school.report.card.line", "report_id", string="Subjects")

    total = fields.Float(string="Total Marks", readonly=True)
    average = fields.Float(string="Average Percentage", readonly=True)

    state = fields.Selection([
        ("draft", "Draft"),
        ("confirmed", "Confirmed"),
        ("published", "Published"),
    ], default="draft", tracking=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    _sql_constraints = [
        ("unique_report", "unique(student_id, term, academic_year_id)",
         "Report card already exists for this student in this term and academic year!")
    ]

    @api.depends("student_id.name", "term", "academic_year_id.name")
    def _compute_name(self):
        for rec in self:
            term_name = dict(self._fields["term"].selection).get(rec.term, "")
            rec.name = f"{rec.student_id.name} - {term_name} - {rec.academic_year_id.name}"

    def _calculate_totals(self):
        """Calculate total marks and average percentage from lines."""
        self.ensure_one()
        if self.line_ids:
            total = sum(self.line_ids.mapped("total_mark"))
            percentages = [line.percentage for line in self.line_ids if line.percentage > 0]
            average = sum(percentages) / len(percentages) if percentages else 0.0
            
            # Update directly without triggering computed fields
            self.env.cr.execute("""
                UPDATE school_report_card 
                SET total = %s, average = %s
                WHERE id = %s
            """, (total, average, self.id))
            
            # Invalidate cache
            self.invalidate_recordset(['total', 'average'])
        else:
            self.env.cr.execute("""
                UPDATE school_report_card 
                SET total = 0.0, average = 0.0
                WHERE id = %s
            """, (self.id,))
            self.invalidate_recordset(['total', 'average'])

    def action_confirm(self):
        for rec in self:
            if not rec.line_ids:
                raise ValidationError("Cannot confirm report card without subject lines.")
            # Calculate totals before confirming
            rec._calculate_totals()
        self.write({"state": "confirmed"})

    def action_publish(self):
        # Calculate totals before publishing to freeze the values
        for rec in self:
            rec._calculate_totals()
        self.write({"state": "published"})

    def action_set_draft(self):
        self.write({"state": "draft"})

    def action_generate_from_exams(self):
        """
        Pull marks from published exams for the student section + term.
        Aggregates different exam types into single subject line.
        """
        for rec in self:
            exams = self.env["school.exam"].search([
                ("section_id", "=", rec.section_id.id),
                ("term", "=", rec.term),
                ("academic_year_id", "=", rec.academic_year_id.id),
                ("state", "=", "done"),
            ])

            # Group exams by subject
            subject_marks = {}
            for exam in exams:
                mark_line = exam.mark_line_ids.filtered(lambda m: m.student_id == rec.student_id)
                if mark_line:
                    subject_id = exam.subject_id.id
                    if subject_id not in subject_marks:
                        subject_marks[subject_id] = {
                            "subject_id": subject_id,
                            "teacher_id": exam.teacher_id.id,
                            "quiz_mark": 0.0,
                            "quiz_max": 0.0,
                            "mid_mark": 0.0,
                            "mid_max": 0.0,
                            "final_mark": 0.0,
                            "final_max": 0.0,
                            "assignment_mark": 0.0,
                            "assignment_max": 0.0,
                        }
                    
                    # Map exam type to corresponding field
                    exam_type = exam.exam_type
                    if exam_type == "quiz":
                        subject_marks[subject_id]["quiz_mark"] = mark_line[0].mark
                        subject_marks[subject_id]["quiz_max"] = exam.max_mark
                    elif exam_type == "mid":
                        subject_marks[subject_id]["mid_mark"] = mark_line[0].mark
                        subject_marks[subject_id]["mid_max"] = exam.max_mark
                    elif exam_type == "final":
                        subject_marks[subject_id]["final_mark"] = mark_line[0].mark
                        subject_marks[subject_id]["final_max"] = exam.max_mark
                    elif exam_type == "assignment":
                        subject_marks[subject_id]["assignment_mark"] = mark_line[0].mark
                        subject_marks[subject_id]["assignment_max"] = exam.max_mark

            # Create lines
            lines = [(0, 0, vals) for vals in subject_marks.values()]
            
            rec.line_ids.unlink()
            if lines:
                rec.write({"line_ids": lines})
                # Calculate totals after generating lines
                rec._calculate_totals()

class SchoolReportCardLine(models.Model):
    _name = "school.report.card.line"
    _description = "Report Card Line"
    _order = "subject_id"

    report_id = fields.Many2one("school.report.card", required=True, ondelete="cascade")
    subject_id = fields.Many2one("school.subject", required=True)
    teacher_id = fields.Many2one("school.teacher")

    # Individual exam marks (actual marks obtained)
    quiz_mark = fields.Float(string="Quiz")
    quiz_max = fields.Float(string="Quiz Max", default=100.0)
    
    mid_mark = fields.Float(string="Midterm")
    mid_max = fields.Float(string="Midterm Max", default=100.0)
    
    final_mark = fields.Float(string="Final")
    final_max = fields.Float(string="Final Max", default=100.0)
    
    assignment_mark = fields.Float(string="Assignment")
    assignment_max = fields.Float(string="Assignment Max", default=100.0)

    # Computed fields
    total_mark = fields.Float(string="Total Marks", readonly=True)
    total_max = fields.Float(string="Total Max", readonly=True)
    percentage = fields.Float(string="Percentage", readonly=True)
    grade = fields.Char(string="Grade", readonly=True)
    
    remark = fields.Char()

    @api.onchange("quiz_mark", "quiz_max", "mid_mark", "mid_max", 
                  "final_mark", "final_max", "assignment_mark", "assignment_max")
    def _onchange_marks(self):
        """
        Calculate total marks and grade when marks are changed.
        This only runs during data entry, not after the report is saved.
        """
        for rec in self:
            # Sum all marks obtained
            rec.total_mark = rec.quiz_mark + rec.mid_mark + rec.final_mark + rec.assignment_mark
            
            # Calculate total maximum marks (only count exams that were taken)
            max_possible = 0.0
            if rec.quiz_mark > 0 and rec.quiz_max > 0:
                max_possible += rec.quiz_max
            if rec.mid_mark > 0 and rec.mid_max > 0:
                max_possible += rec.mid_max
            if rec.final_mark > 0 and rec.final_max > 0:
                max_possible += rec.final_max
            if rec.assignment_mark > 0 and rec.assignment_max > 0:
                max_possible += rec.assignment_max
            
            rec.total_max = max_possible
            
            # Calculate percentage
            if max_possible > 0:
                rec.percentage = (rec.total_mark / max_possible) * 100
                
                # Assign grade based on percentage
                if rec.percentage >= 90:
                    rec.grade = "A"
                elif rec.percentage >= 75:
                    rec.grade = "B"
                elif rec.percentage >= 60:
                    rec.grade = "C"
                elif rec.percentage >= 50:
                    rec.grade = "D"
                else:
                    rec.grade = "F"
            else:
                rec.percentage = 0.0
                rec.grade = ""

    @api.model_create_multi
    def create(self, vals_list):
        """Calculate grades when creating records."""
        records = super().create(vals_list)
        for record in records:
            record._compute_grade_on_save()
            # Trigger parent report card totals calculation
            if record.report_id:
                record.report_id._calculate_totals()
        return records

    def write(self, vals):
        """Calculate grades when updating records, but only if report is in draft state."""
        result = super().write(vals)
        # Only recalculate if any mark field is being updated and report is in draft
        mark_fields = ['quiz_mark', 'quiz_max', 'mid_mark', 'mid_max', 
                       'final_mark', 'final_max', 'assignment_mark', 'assignment_max']
        if any(field in vals for field in mark_fields):
            for record in self:
                if record.report_id.state == 'draft':
                    record._compute_grade_on_save()
                    # Trigger parent report card totals calculation
                    record.report_id._calculate_totals()
        return result

    def _compute_grade_on_save(self):
        """Helper method to calculate and save grade values."""
        self.ensure_one()
        
        # Sum all marks obtained
        total_mark = self.quiz_mark + self.mid_mark + self.final_mark + self.assignment_mark
        
        # Calculate total maximum marks (only count exams that were taken)
        max_possible = 0.0
        if self.quiz_mark > 0 and self.quiz_max > 0:
            max_possible += self.quiz_max
        if self.mid_mark > 0 and self.mid_max > 0:
            max_possible += self.mid_max
        if self.final_mark > 0 and self.final_max > 0:
            max_possible += self.final_max
        if self.assignment_mark > 0 and self.assignment_max > 0:
            max_possible += self.assignment_max
        
        # Calculate percentage and grade
        if max_possible > 0:
            percentage = (total_mark / max_possible) * 100
            
            # Assign grade based on percentage
            if percentage >= 90:
                grade = "A"
            elif percentage >= 75:
                grade = "B"
            elif percentage >= 60:
                grade = "C"
            elif percentage >= 50:
                grade = "D"
            else:
                grade = "F"
        else:
            percentage = 0.0
            grade = ""
        
        # Update fields directly without triggering write
        self.env.cr.execute("""
            UPDATE school_report_card_line 
            SET total_mark = %s, total_max = %s, percentage = %s, grade = %s
            WHERE id = %s
        """, (total_mark, max_possible, percentage, grade, self.id))
        
        # Invalidate cache to reflect the changes
        self.invalidate_recordset(['total_mark', 'total_max', 'percentage', 'grade'])

    @api.constrains("subject_id", "report_id")
    def _check_duplicate_subject(self):
        for rec in self:
            domain = [
                ("id", "!=", rec.id),
                ("report_id", "=", rec.report_id.id),
                ("subject_id", "=", rec.subject_id.id),
            ]
            if self.search_count(domain):
                raise ValidationError("Duplicate subject in report card is not allowed.")
