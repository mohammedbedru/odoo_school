from odoo import models, fields, api

class AcademicAnalytics(models.Model):
    _name = "school.academic.analytics"
    _description = "Academic Performance Analytics"
    
    name = fields.Char(compute='_compute_name', store=True)
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)
    term = fields.Selection([
        ('t1', 'Term 1'),
        ('t2', 'Term 2'),
        ('t3', 'Term 3'),
    ], string='Term', required=True)
    grade_id = fields.Many2one('school.grade', string='Grade')
    section_id = fields.Many2one('school.section', string='Section')
    
    # Performance metrics
    total_students = fields.Integer(compute='_compute_metrics', string='Total Students', store=True)
    students_with_grades = fields.Integer(compute='_compute_metrics', string='Students with Grades', store=True)
    
    grade_a_count = fields.Integer(compute='_compute_metrics', string='Grade A', store=True)
    grade_b_count = fields.Integer(compute='_compute_metrics', string='Grade B', store=True)
    grade_c_count = fields.Integer(compute='_compute_metrics', string='Grade C', store=True)
    grade_d_count = fields.Integer(compute='_compute_metrics', string='Grade D', store=True)
    grade_f_count = fields.Integer(compute='_compute_metrics', string='Grade F', store=True)
    
    average_percentage = fields.Float(compute='_compute_metrics', string='Average %', store=True)
    pass_percentage = fields.Float(compute='_compute_metrics', string='Pass %', store=True)
    
    # Attendance metrics
    total_attendance_records = fields.Integer(compute='_compute_metrics', string='Attendance Records', store=True)
    present_count = fields.Integer(compute='_compute_metrics', string='Present', store=True)
    absent_count = fields.Integer(compute='_compute_metrics', string='Absent', store=True)
    late_count = fields.Integer(compute='_compute_metrics', string='Late', store=True)
    attendance_rate = fields.Float(compute='_compute_metrics', string='Attendance Rate %', store=True)
    
    @api.depends('academic_year_id', 'term', 'grade_id', 'section_id')
    def _compute_name(self):
        for rec in self:
            parts = [rec.academic_year_id.name, dict(rec._fields['term'].selection).get(rec.term, '')]
            if rec.grade_id:
                parts.append(rec.grade_id.name)
            if rec.section_id:
                parts.append(rec.section_id.name)
            rec.name = ' - '.join(parts)
    
    @api.depends('academic_year_id', 'term', 'grade_id', 'section_id')
    def _compute_metrics(self):
        for rec in self:
            # Build domain for students
            student_domain = [
                ('academic_year_id', '=', rec.academic_year_id.id),
                ('status', 'in', ['enrolled', 'active'])
            ]
            if rec.grade_id:
                student_domain.append(('grade_id', '=', rec.grade_id.id))
            if rec.section_id:
                student_domain.append(('section_id', '=', rec.section_id.id))
            
            students = self.env['school.student'].search(student_domain)
            rec.total_students = len(students)
            
            # Get report cards
            report_domain = [
                ('student_id', 'in', students.ids),
                ('academic_year_id', '=', rec.academic_year_id.id),
                ('term', '=', rec.term),
                ('state', '=', 'published')
            ]
            
            report_cards = self.env['school.report.card'].search(report_domain)
            rec.students_with_grades = len(report_cards)
            
            # Grade distribution
            if report_cards:
                rec.grade_a_count = len(report_cards.filtered(lambda r: r.final_grade == 'A'))
                rec.grade_b_count = len(report_cards.filtered(lambda r: r.final_grade == 'B'))
                rec.grade_c_count = len(report_cards.filtered(lambda r: r.final_grade == 'C'))
                rec.grade_d_count = len(report_cards.filtered(lambda r: r.final_grade == 'D'))
                rec.grade_f_count = len(report_cards.filtered(lambda r: r.final_grade == 'F'))
                
                # Average percentage
                rec.average_percentage = sum(report_cards.mapped('weighted_average')) / len(report_cards)
                
                # Pass percentage (assuming D and above is pass)
                passed = len(report_cards.filtered(lambda r: r.final_grade in ['A', 'B', 'C', 'D']))
                rec.pass_percentage = (passed / len(report_cards) * 100) if report_cards else 0.0
            else:
                rec.grade_a_count = 0
                rec.grade_b_count = 0
                rec.grade_c_count = 0
                rec.grade_d_count = 0
                rec.grade_f_count = 0
                rec.average_percentage = 0.0
                rec.pass_percentage = 0.0
            
            # Attendance metrics
            attendance_domain = [
                ('student_id', 'in', students.ids)
            ]
            attendance_lines = self.env['school.attendance.line'].search(attendance_domain)
            
            rec.total_attendance_records = len(attendance_lines)
            rec.present_count = len(attendance_lines.filtered(lambda a: a.status == 'present'))
            rec.absent_count = len(attendance_lines.filtered(lambda a: a.status == 'absent'))
            rec.late_count = len(attendance_lines.filtered(lambda a: a.status == 'late'))
            
            if attendance_lines:
                rec.attendance_rate = (rec.present_count / len(attendance_lines) * 100)
            else:
                rec.attendance_rate = 0.0


class SubjectPerformance(models.Model):
    _name = "school.subject.performance"
    _description = "Subject-wise Performance Analytics"
    
    name = fields.Char(compute='_compute_name', store=True)
    subject_id = fields.Many2one('school.subject', string='Subject', required=True)
    academic_year_id = fields.Many2one('school.academic.year', string='Academic Year', required=True)
    term = fields.Selection([
        ('t1', 'Term 1'),
        ('t2', 'Term 2'),
        ('t3', 'Term 3'),
    ], string='Term', required=True)
    grade_id = fields.Many2one('school.grade', string='Grade')
    
    total_students = fields.Integer(compute='_compute_performance', string='Total Students', store=True)
    average_marks = fields.Float(compute='_compute_performance', string='Average Marks', store=True)
    highest_marks = fields.Float(compute='_compute_performance', string='Highest Marks', store=True)
    lowest_marks = fields.Float(compute='_compute_performance', string='Lowest Marks', store=True)
    pass_count = fields.Integer(compute='_compute_performance', string='Passed', store=True)
    fail_count = fields.Integer(compute='_compute_performance', string='Failed', store=True)
    pass_percentage = fields.Float(compute='_compute_performance', string='Pass %', store=True)
    
    @api.depends('subject_id', 'academic_year_id', 'term', 'grade_id')
    def _compute_name(self):
        for rec in self:
            parts = [rec.subject_id.name, rec.academic_year_id.name, dict(rec._fields['term'].selection).get(rec.term, '')]
            if rec.grade_id:
                parts.append(rec.grade_id.name)
            rec.name = ' - '.join(parts)
    
    @api.depends('subject_id', 'academic_year_id', 'term', 'grade_id')
    def _compute_performance(self):
        for rec in self:
            # Get all report card lines for this subject
            domain = [
                ('subject_id', '=', rec.subject_id.id),
                ('report_card_id.academic_year_id', '=', rec.academic_year_id.id),
                ('report_card_id.term', '=', rec.term),
                ('report_card_id.state', '=', 'published')
            ]
            
            if rec.grade_id:
                domain.append(('report_card_id.student_id.grade_id', '=', rec.grade_id.id))
            
            lines = self.env['school.report.card.line'].search(domain)
            
            if lines:
                rec.total_students = len(lines)
                
                # Calculate total marks for each student
                total_marks = []
                for line in lines:
                    total = (line.quiz_mark or 0) + (line.mid_mark or 0) + (line.final_mark or 0) + (line.assignment_mark or 0)
                    total_marks.append(total)
                
                rec.average_marks = sum(total_marks) / len(total_marks) if total_marks else 0.0
                rec.highest_marks = max(total_marks) if total_marks else 0.0
                rec.lowest_marks = min(total_marks) if total_marks else 0.0
                
                # Pass/Fail (assuming 60% is pass)
                pass_threshold = 0.6
                passed = sum(1 for line in lines if line.percentage >= pass_threshold * 100)
                rec.pass_count = passed
                rec.fail_count = len(lines) - passed
                rec.pass_percentage = (passed / len(lines) * 100) if lines else 0.0
            else:
                rec.total_students = 0
                rec.average_marks = 0.0
                rec.highest_marks = 0.0
                rec.lowest_marks = 0.0
                rec.pass_count = 0
                rec.fail_count = 0
                rec.pass_percentage = 0.0


class AttendanceAnalytics(models.Model):
    _name = "school.attendance.analytics"
    _description = "Attendance Analytics"
    _auto = False
    _rec_name = "grade_id"
    
    grade_id = fields.Many2one('school.grade', string='Grade', readonly=True)
    section_id = fields.Many2one('school.section', string='Section', readonly=True)
    attendance_date = fields.Date(string='Date', readonly=True)
    
    total_students = fields.Integer(string='Total Students', readonly=True)
    present_count = fields.Integer(string='Present', readonly=True)
    absent_count = fields.Integer(string='Absent', readonly=True)
    late_count = fields.Integer(string='Late', readonly=True)
    attendance_rate = fields.Float(string='Attendance %', readonly=True)
    
    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW school_attendance_analytics AS (
                SELECT
                    ROW_NUMBER() OVER() as id,
                    s.grade_id,
                    s.section_id,
                    a.date as attendance_date,
                    COUNT(DISTINCT al.student_id) as total_students,
                    SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END) as present_count,
                    SUM(CASE WHEN al.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
                    SUM(CASE WHEN al.status = 'late' THEN 1 ELSE 0 END) as late_count,
                    CASE 
                        WHEN COUNT(*) > 0 
                        THEN (SUM(CASE WHEN al.status = 'present' THEN 1 ELSE 0 END)::float / COUNT(*) * 100)
                        ELSE 0 
                    END as attendance_rate
                FROM school_attendance a
                JOIN school_attendance_line al ON al.attendance_id = a.id
                JOIN school_student s ON s.id = al.student_id
                WHERE a.date IS NOT NULL
                GROUP BY s.grade_id, s.section_id, a.date
            )
        """)
