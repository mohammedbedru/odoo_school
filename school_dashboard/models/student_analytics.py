from odoo import models, fields, api
from datetime import datetime

class StudentAnalytics(models.Model):
    _name = "school.student.analytics"
    _description = "Student Analytics"
    _auto = False
    _rec_name = "grade_id"
    
    grade_id = fields.Many2one('school.grade', string='Grade', readonly=True)
    section_id = fields.Many2one('school.section', string='Section', readonly=True)
    student_count = fields.Integer(string='Student Count', readonly=True)
    male_count = fields.Integer(string='Male Students', readonly=True)
    female_count = fields.Integer(string='Female Students', readonly=True)
    average_age = fields.Float(string='Average Age', readonly=True)
    status = fields.Selection([
        ('draft', 'Applicant'),
        ('enrolled', 'Enrolled'),
        ('active', 'Active'),
        ('graduated', 'Graduated'),
        ('dropped', 'Dropped'),
    ], string='Status', readonly=True)
    
    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW school_student_analytics AS (
                SELECT
                    ROW_NUMBER() OVER() as id,
                    grade_id,
                    section_id,
                    status,
                    COUNT(*) as student_count,
                    SUM(CASE WHEN gender = 'male' THEN 1 ELSE 0 END) as male_count,
                    SUM(CASE WHEN gender = 'female' THEN 1 ELSE 0 END) as female_count,
                    AVG(age) as average_age
                FROM school_student
                WHERE active = true
                GROUP BY grade_id, section_id, status
            )
        """)
    
    def action_view_students(self):
        self.ensure_one()
        domain = []
        if self.grade_id:
            domain.append(('grade_id', '=', self.grade_id.id))
        if self.section_id:
            domain.append(('section_id', '=', self.section_id.id))
        if self.status:
            domain.append(('status', '=', self.status))
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'school.student',
            'view_mode': 'list,form',
            'domain': domain,
        }


class GradeAnalytics(models.Model):
    _name = "school.grade.analytics"
    _description = "Grade-wise Analytics"
    
    name = fields.Char(compute='_compute_name', store=True)
    grade_id = fields.Many2one('school.grade', string='Grade', required=True)
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)
    
    # Student metrics
    total_students = fields.Integer(compute='_compute_metrics', string='Total Students', store=True)
    male_students = fields.Integer(compute='_compute_metrics', string='Male Students', store=True)
    female_students = fields.Integer(compute='_compute_metrics', string='Female Students', store=True)
    
    # Academic metrics
    average_attendance = fields.Float(compute='_compute_metrics', string='Average Attendance %', store=True)
    total_exams = fields.Integer(compute='_compute_metrics', string='Total Exams', store=True)
    average_grade = fields.Char(compute='_compute_metrics', string='Average Grade', store=True)
    
    # Fee metrics
    total_fees = fields.Monetary(compute='_compute_metrics', string='Total Fees', store=True, currency_field='currency_id')
    collected_fees = fields.Monetary(compute='_compute_metrics', string='Collected Fees', store=True, currency_field='currency_id')
    pending_fees = fields.Monetary(compute='_compute_metrics', string='Pending Fees', store=True, currency_field='currency_id')
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    
    @api.depends('grade_id', 'academic_year_id')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{rec.grade_id.name} - {rec.academic_year_id.name}"
    
    @api.depends('grade_id', 'academic_year_id')
    def _compute_metrics(self):
        for rec in self:
            # Student metrics
            students = self.env['school.student'].search([
                ('grade_id', '=', rec.grade_id.id),
                ('academic_year_id', '=', rec.academic_year_id.id),
                ('status', 'in', ['enrolled', 'active'])
            ])
            
            rec.total_students = len(students)
            rec.male_students = len(students.filtered(lambda s: s.gender == 'male'))
            rec.female_students = len(students.filtered(lambda s: s.gender == 'female'))
            
            # Attendance metrics
            attendances = self.env['school.attendance.line'].search([
                ('student_id', 'in', students.ids)
            ])
            if attendances:
                present_count = len(attendances.filtered(lambda a: a.status == 'present'))
                rec.average_attendance = (present_count / len(attendances) * 100) if attendances else 0.0
            else:
                rec.average_attendance = 0.0
            
            # Exam metrics
            sections = self.env['school.section'].search([('grade_id', '=', rec.grade_id.id)])
            rec.total_exams = self.env['school.exam'].search_count([
                ('section_id', 'in', sections.ids),
                ('academic_year_id', '=', rec.academic_year_id.id)
            ])
            
            # Average grade calculation
            report_cards = self.env['school.report.card'].search([
                ('student_id', 'in', students.ids),
                ('academic_year_id', '=', rec.academic_year_id.id)
            ])
            if report_cards:
                avg_percentage = sum(report_cards.mapped('weighted_average')) / len(report_cards)
                rec.average_grade = rec._get_grade_from_percentage(avg_percentage)
            else:
                rec.average_grade = 'N/A'
            
            # Fee metrics
            fees = self.env['school.student.fee'].search([
                ('student_id', 'in', students.ids),
                ('academic_year_id', '=', rec.academic_year_id.id)
            ])
            rec.total_fees = sum(fees.mapped('amount_total')) + sum(fees.mapped('amount_paid'))
            rec.collected_fees = sum(fees.mapped('amount_paid'))
            rec.pending_fees = sum(fees.mapped('amount_due'))
    
    def _get_grade_from_percentage(self, percentage):
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
