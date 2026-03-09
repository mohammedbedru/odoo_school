from odoo import models, fields, api
from datetime import datetime, timedelta

class SchoolDashboard(models.Model):
    _name = "school.dashboard"
    _description = "School Dashboard Main"
    
    name = fields.Char(default="School Dashboard", readonly=True)
    
    # Student Statistics
    total_students = fields.Integer(compute='_compute_student_stats', string='Total Students')
    active_students = fields.Integer(compute='_compute_student_stats', string='Active Students')
    new_admissions_month = fields.Integer(compute='_compute_student_stats', string='New Admissions (This Month)')
    male_students = fields.Integer(compute='_compute_student_stats', string='Male Students')
    female_students = fields.Integer(compute='_compute_student_stats', string='Female Students')
    
    # Fee Statistics
    total_fees_collected = fields.Monetary(compute='_compute_fee_stats', string='Total Fees Collected', currency_field='currency_id')
    total_fees_pending = fields.Monetary(compute='_compute_fee_stats', string='Total Fees Pending', currency_field='currency_id')
    fees_collected_month = fields.Monetary(compute='_compute_fee_stats', string='Fees Collected (This Month)', currency_field='currency_id')
    overdue_fees = fields.Monetary(compute='_compute_fee_stats', string='Overdue Fees', currency_field='currency_id')
    collection_rate = fields.Float(compute='_compute_fee_stats', string='Collection Rate (%)')
    
    # Academic Statistics
    total_exams = fields.Integer(compute='_compute_academic_stats', string='Total Exams')
    exams_this_month = fields.Integer(compute='_compute_academic_stats', string='Exams This Month')
    average_attendance_rate = fields.Float(compute='_compute_academic_stats', string='Average Attendance (%)')
    total_classes = fields.Integer(compute='_compute_academic_stats', string='Total Classes')
    
    # Staff Statistics
    total_teachers = fields.Integer(compute='_compute_staff_stats', string='Total Teachers')
    
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    
    @api.depends_context('company')
    def _compute_student_stats(self):
        for rec in self:
            Student = self.env['school.student']
            
            # Total and active students
            rec.total_students = Student.search_count([])
            rec.active_students = Student.search_count([('status', 'in', ['enrolled', 'active'])])
            
            # New admissions this month
            first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            rec.new_admissions_month = Student.search_count([
                ('admission_date', '>=', first_day_month.date())
            ])
            
            # Gender distribution
            rec.male_students = Student.search_count([('gender', '=', 'male'), ('status', 'in', ['enrolled', 'active'])])
            rec.female_students = Student.search_count([('gender', '=', 'female'), ('status', 'in', ['enrolled', 'active'])])
    
    @api.depends_context('company')
    def _compute_fee_stats(self):
        for rec in self:
            Fee = self.env['school.student.fee']
            
            # Total fees
            all_fees = Fee.search([])
            rec.total_fees_collected = sum(all_fees.mapped('amount_paid'))
            rec.total_fees_pending = sum(all_fees.mapped('amount_due'))
            
            # Fees collected this month
            first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            invoices_this_month = self.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', first_day_month.date()),
                ('payment_state', '=', 'paid')
            ])
            rec.fees_collected_month = sum(invoices_this_month.mapped('amount_total'))
            
            # Overdue fees
            overdue_fees = Fee.search([('is_overdue', '=', True)])
            rec.overdue_fees = sum(overdue_fees.mapped('amount_due'))
            
            # Collection rate
            total_amount = rec.total_fees_collected + rec.total_fees_pending
            if total_amount > 0:
                rec.collection_rate = (rec.total_fees_collected / total_amount) * 100
            else:
                rec.collection_rate = 0.0
    
    @api.depends_context('company')
    def _compute_academic_stats(self):
        for rec in self:
            Exam = self.env['school.exam']
            AttendanceLine = self.env['school.attendance.line']
            Section = self.env['school.section']
            
            # Exam statistics
            rec.total_exams = Exam.search_count([])
            
            first_day_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            rec.exams_this_month = Exam.search_count([
                ('exam_date', '>=', first_day_month.date())
            ])
            
            # Attendance rate
            attendance_lines = AttendanceLine.search([])
            if attendance_lines:
                total_present = sum(1 for att in attendance_lines if att.status == 'present')
                total_records = len(attendance_lines)
                rec.average_attendance_rate = (total_present / total_records * 100) if total_records > 0 else 0.0
            else:
                rec.average_attendance_rate = 0.0
            
            # Total classes
            rec.total_classes = Section.search_count([])
    
    @api.depends_context('company')
    def _compute_staff_stats(self):
        for rec in self:
            # Count teachers (users with teacher group)
            teacher_group = self.env.ref('school_core.group_school_teacher', raise_if_not_found=False)
            if teacher_group:
                rec.total_teachers = len(teacher_group.users)
            else:
                rec.total_teachers = 0
    
    def action_view_students(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Students',
            'res_model': 'school.student',
            'view_mode': 'list,form',
            'domain': [('status', 'in', ['enrolled', 'active'])],
        }
    
    def action_view_fees(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Student Fees',
            'res_model': 'school.student.fee',
            'view_mode': 'list,form',
        }
    
    def action_view_overdue_fees(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Overdue Fees',
            'res_model': 'school.student.fee',
            'view_mode': 'list,form',
            'domain': [('is_overdue', '=', True)],
        }
    
    def action_view_exams(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Exams',
            'res_model': 'school.exam',
            'view_mode': 'list,form',
        }
