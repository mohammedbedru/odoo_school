from odoo import http
from odoo.http import request
from datetime import datetime, timedelta
import json


class SchoolDashboardController(http.Controller):
    
    @http.route('/school/dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """Get all dashboard data in one call"""
        return {
            'kpis': self._get_kpis(),
            'student_stats': self._get_student_stats(),
            'fee_stats': self._get_fee_stats(),
            'academic_stats': self._get_academic_stats(),
            'charts': self._get_chart_data(),
        }
        # return request.make_json_response(data)
    
    def _get_kpis(self):
        """Get Key Performance Indicators"""
        Student = request.env['school.student']
        Fee = request.env['school.student.fee']
        AttendanceLine = request.env['school.attendance.line']
        
        # Student KPIs
        total_students = Student.search_count([])
        active_students = Student.search_count([('status', 'in', ['enrolled', 'active'])])
        
        # Fee KPIs
        all_fees = Fee.search([])
        total_collected = sum(all_fees.mapped('amount_paid'))
        total_pending = sum(all_fees.mapped('amount_due'))
        collection_rate = (total_collected / (total_collected + total_pending) * 100) if (total_collected + total_pending) > 0 else 0
        
        # Attendance KPI
        attendance_lines = AttendanceLine.search([])
        if attendance_lines:
            present = len(attendance_lines.filtered(lambda a: a.status == 'present'))
            attendance_rate = (present / len(attendance_lines) * 100)
        else:
            attendance_rate = 0
        
        return {
            'total_students': total_students,
            'active_students': active_students,
            'total_collected': total_collected,
            'total_pending': total_pending,
            'collection_rate': round(collection_rate, 2),
            'attendance_rate': round(attendance_rate, 2),
        }
    
    def _get_student_stats(self):
        """Get student statistics"""
        Student = request.env['school.student']
        
        # Gender distribution
        male_count = Student.search_count([('gender', '=', 'male'), ('status', 'in', ['enrolled', 'active'])])
        female_count = Student.search_count([('gender', '=', 'female'), ('status', 'in', ['enrolled', 'active'])])
        
        # Grade distribution
        grades = request.env['school.grade'].search([])
        grade_distribution = []
        for grade in grades:
            count = Student.search_count([
                ('grade_id', '=', grade.id),
                ('status', 'in', ['enrolled', 'active'])
            ])
            if count > 0:
                grade_distribution.append({
                    'name': grade.name,
                    'count': count
                })
        
        # New admissions this month
        first_day = datetime.now().replace(day=1).date()
        new_admissions = Student.search_count([('admission_date', '>=', first_day)])
        
        return {
            'gender': {
                'male': male_count,
                'female': female_count,
            },
            'grade_distribution': grade_distribution,
            'new_admissions': new_admissions,
        }
    
    def _get_fee_stats(self):
        """Get fee statistics"""
        Fee = request.env['school.student.fee']
        
        # Overdue fees
        overdue_fees = Fee.search([('is_overdue', '=', True)])
        overdue_amount = sum(overdue_fees.mapped('amount_due'))
        overdue_count = len(overdue_fees)
        
        # Payment status distribution
        paid_count = Fee.search_count([('payment_state', '=', 'paid')])
        partial_count = Fee.search_count([('payment_state', '=', 'partial')])
        unpaid_count = Fee.search_count([('payment_state', '=', 'not_paid')])
        
        # Monthly collection trend (last 6 months)
        monthly_trend = []
        for i in range(5, -1, -1):
            date = datetime.now() - timedelta(days=30*i)
            first_day = date.replace(day=1).date()
            if date.month == 12:
                last_day = date.replace(year=date.year + 1, month=1, day=1).date() - timedelta(days=1)
            else:
                last_day = date.replace(month=date.month + 1, day=1).date() - timedelta(days=1)
            
            invoices = request.env['account.move'].search([
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', first_day),
                ('invoice_date', '<=', last_day),
                ('payment_state', '=', 'paid')
            ])
            
            monthly_trend.append({
                'month': date.strftime('%b %Y'),
                'amount': sum(invoices.mapped('amount_total'))
            })
        
        return {
            'overdue_amount': overdue_amount,
            'overdue_count': overdue_count,
            'payment_status': {
                'paid': paid_count,
                'partial': partial_count,
                'unpaid': unpaid_count,
            },
            'monthly_trend': monthly_trend,
        }
    
    def _get_academic_stats(self):
        """Get academic statistics"""
        ReportCard = request.env['school.report.card']
        ReportCardLine = request.env['school.report.card.line']
        Exam = request.env['school.exam']
        
        # Grade distribution from report card lines
        published_cards = ReportCard.search([('state', '=', 'published')])
        all_lines = ReportCardLine.search([('report_id', 'in', published_cards.ids)])
        
        grade_distribution = {
            'A': len(all_lines.filtered(lambda r: r.grade == 'A')),
            'B': len(all_lines.filtered(lambda r: r.grade == 'B')),
            'C': len(all_lines.filtered(lambda r: r.grade == 'C')),
            'D': len(all_lines.filtered(lambda r: r.grade == 'D')),
            'F': len(all_lines.filtered(lambda r: r.grade == 'F')),
        }
        
        # Average performance from report cards
        if published_cards:
            avg_percentage = sum(published_cards.mapped('average')) / len(published_cards)
        else:
            avg_percentage = 0
        
        # Upcoming exams
        upcoming_exams = Exam.search([
            ('date', '>=', datetime.now().date())
        ], order='date asc', limit=5)
        
        upcoming_list = [{
            'name': exam.name,
            'date': exam.date.strftime('%Y-%m-%d'),
            'subject': exam.subject_id.name if exam.subject_id else 'N/A',
        } for exam in upcoming_exams]
        
        return {
            'grade_distribution': grade_distribution,
            'average_percentage': round(avg_percentage, 2),
            'upcoming_exams': upcoming_list,
        }
    
    def _get_chart_data(self):
        """Get data for various charts"""
        return {
            'student_growth': self._get_student_growth_data(),
            'fee_collection': self._get_fee_collection_data(),
            'attendance_trend': self._get_attendance_trend_data(),
        }
    
    def _get_student_growth_data(self):
        """Student enrollment growth over last 12 months"""
        Student = request.env['school.student']
        data = []
        
        for i in range(11, -1, -1):
            date = datetime.now() - timedelta(days=30*i)
            first_day = date.replace(day=1).date()
            
            count = Student.search_count([
                ('admission_date', '<=', first_day)
            ])
            
            data.append({
                'month': date.strftime('%b'),
                'count': count
            })
        
        return data
    
    def _get_fee_collection_data(self):
        """Fee collection by grade"""
        Grade = request.env['school.grade']
        Fee = request.env['school.student.fee']
        
        data = []
        for grade in Grade.search([]):
            students = request.env['school.student'].search([('grade_id', '=', grade.id)])
            fees = Fee.search([('student_id', 'in', students.ids)])
            
            collected = sum(fees.mapped('amount_paid'))
            pending = sum(fees.mapped('amount_due'))
            
            if collected > 0 or pending > 0:
                data.append({
                    'grade': grade.name,
                    'collected': collected,
                    'pending': pending,
                })
        
        return data
    
    def _get_attendance_trend_data(self):
        """Attendance trend for last 30 days"""
        Attendance = request.env['school.attendance']
        data = []
        
        for i in range(29, -1, -1):
            date = (datetime.now() - timedelta(days=i)).date()
            
            attendances = Attendance.search([('date', '=', date)])
            if attendances:
                total_lines = sum(len(att.line_ids) for att in attendances)
                present_lines = sum(len(att.line_ids.filtered(lambda l: l.status == 'present')) for att in attendances)
                rate = (present_lines / total_lines * 100) if total_lines > 0 else 0
            else:
                rate = 0
            
            data.append({
                'date': date.strftime('%m/%d'),
                'rate': round(rate, 1)
            })
        
        return data
    
    @http.route('/school/dashboard/refresh', type='json', auth='user')
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        return {
            'kpis': self._get_kpis(),
            'student_stats': self._get_student_stats(),
            'fee_stats': self._get_fee_stats(),
            'academic_stats': self._get_academic_stats(),
            'charts': self._get_chart_data(),
        }
        # return request.make_json_response(data)
    
    @http.route('/school/dashboard/student/<int:student_id>', type='json', auth='user')
    def get_student_details(self, student_id):
        """Get detailed student information"""
        student = request.env['school.student'].browse(student_id)
        if not student.exists():
            return request.make_json_response({'error': 'Student not found'})
        
        return {
            'id': student.id,
            'name': student.name,
            'code': student.student_code,
            'grade': student.grade_id.name if student.grade_id else 'N/A',
            'section': student.section_id.name if student.section_id else 'N/A',
            'status': student.status,
            'gender': student.gender,
            'age': student.age,
        }
        # return request.make_json_response(data)
