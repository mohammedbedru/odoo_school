from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from datetime import datetime, timedelta


class StudentPortalController(http.Controller):

    def _get_student(self):
        """Get current student or raise error"""
        student = request.env['school.student'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not student:
            raise AccessError("You are not registered as a student")
        
        return student

    @http.route(['/my/student/profile'], type='http', auth='user', website=True)
    def student_profile(self, **kw):
        """Student profile page"""
        student = self._get_student()
        
        values = {
            'student': student,
            'page_name': 'student_profile',
        }
        
        return request.render('school_portal.student_profile', values)

    @http.route(['/my/student/dashboard'], type='http', auth='user', website=True)
    def student_dashboard(self, **kw):
        """Student academic dashboard"""
        student = self._get_student()
        
        # Get latest report card
        latest_report = request.env['school.report.card'].search([
            ('student_id', '=', student.id),
            ('state', '=', 'published')
        ], order='academic_year_id desc, term desc', limit=1)
        
        # Calculate attendance percentage
        attendance_lines = request.env['school.attendance.line'].search([
            ('student_id', '=', student.id)
        ])
        
        if attendance_lines:
            present_count = len(attendance_lines.filtered(lambda a: a.status == 'present'))
            attendance_percentage = (present_count / len(attendance_lines)) * 100
        else:
            attendance_percentage = 0
        
        # Get upcoming exams
        upcoming_exams = request.env['school.exam'].sudo().search([
            ('section_id', '=', student.section_id.id),
            ('date', '>=', datetime.now().date())
        ], order='date asc', limit=5)
        
        # Calculate rank (if enabled)
        rank = None
        total_students = None
        if latest_report and latest_report.section_id:
            section_reports = request.env['school.report.card'].search([
                ('section_id', '=', latest_report.section_id.id),
                ('term', '=', latest_report.term),
                ('academic_year_id', '=', latest_report.academic_year_id.id),
                ('state', '=', 'published')
            ], order='average desc')
            
            total_students = len(section_reports)
            for idx, report in enumerate(section_reports, 1):
                if report.id == latest_report.id:
                    rank = idx
                    break
        
        values = {
            'student': student,
            'latest_report': latest_report,
            'gpa': latest_report.average if latest_report else 0,
            'attendance_percentage': round(attendance_percentage, 2),
            'upcoming_exams': upcoming_exams,
            'rank': rank,
            'total_students': total_students,
            'page_name': 'student_dashboard',
        }
        
        return request.render('school_portal.student_dashboard', values)

    @http.route(['/my/student/timetable'], type='http', auth='user', website=True)
    def student_timetable(self, **kw):
        """Student timetable page"""
        student = self._get_student()
        
        # Get confirmed timetable for student's section
        timetable = request.env['school.timetable'].sudo().search([
            ('section_id', '=', student.section_id.id),
            ('state', '=', 'confirmed')
        ], limit=1)
        
        # Prepare timetable data
        days = [
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday'),
        ]
        
        # Get unique periods (time slots)
        time_slots = []
        if timetable:
            periods = timetable.line_ids.mapped('period')
            time_slots = sorted(set(periods))
        
        values = {
            'student': student,
            'timetable': timetable,
            'days': days,
            'time_slots': time_slots,
            'page_name': 'student_timetable',
        }
        
        return request.render('school_portal.student_timetable', values)

    @http.route(['/my/student/attendance'], type='http', auth='user', website=True)
    def student_attendance(self, **kw):
        """Student attendance page"""
        student = self._get_student()
        
        # Get attendance records - order by id desc as proxy for date
        attendance_lines = request.env['school.attendance.line'].search([
            ('student_id', '=', student.id)
        ], order='id desc', limit=100)
        
        # Sort by attendance date in Python
        attendance_lines = attendance_lines.sorted(lambda l: l.attendance_id.date, reverse=True)
        
        # Calculate statistics
        total = len(attendance_lines)
        present = len(attendance_lines.filtered(lambda a: a.status == 'present'))
        absent = len(attendance_lines.filtered(lambda a: a.status == 'absent'))
        late = len(attendance_lines.filtered(lambda a: a.status == 'late'))
        excused = len(attendance_lines.filtered(lambda a: a.status == 'excused'))
        
        attendance_percentage = (present / total * 100) if total > 0 else 0
        
        values = {
            'student': student,
            'attendance_lines': attendance_lines,
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'attendance_percentage': round(attendance_percentage, 2),
            'page_name': 'student_attendance',
        }
        
        return request.render('school_portal.student_attendance', values)

    @http.route(['/my/student/marks'], type='http', auth='user', website=True)
    def student_marks(self, **kw):
        """Student exam marks page"""
        student = self._get_student()
        
        # Get exam marks
        exam_marks = request.env['school.exam.mark'].search([
            ('student_id', '=', student.id)
        ], order='id desc')
        
        # Sort by exam date in Python
        exam_marks = exam_marks.sorted(lambda m: m.exam_id.date, reverse=True)
        
        values = {
            'student': student,
            'exam_marks': exam_marks,
            'page_name': 'student_marks',
        }
        
        return request.render('school_portal.student_marks', values)

    @http.route(['/my/student/report-cards'], type='http', auth='user', website=True)
    def student_report_cards(self, **kw):
        """Student report cards list"""
        student = self._get_student()
        
        # Get published report cards
        report_cards = request.env['school.report.card'].search([
            ('student_id', '=', student.id),
            ('state', '=', 'published')
        ], order='academic_year_id desc, term desc')
        
        values = {
            'student': student,
            'report_cards': report_cards,
            'page_name': 'student_report_cards',
        }
        
        return request.render('school_portal.student_report_cards', values)

    @http.route(['/my/student/report-card/<int:report_id>'], type='http', auth='user', website=True)
    def student_report_card_detail(self, report_id, **kw):
        """Student report card detail"""
        student = self._get_student()
        
        report_card = request.env['school.report.card'].browse(report_id)
        
        # Security check
        if report_card.student_id.id != student.id:
            raise AccessError("You can only view your own report cards")
        
        values = {
            'student': student,
            'report_card': report_card,
            'page_name': 'student_report_cards',
        }
        
        return request.render('school_portal.student_report_card_detail', values)

    @http.route(['/my/student/report-card/<int:report_id>/pdf'], type='http', auth='user')
    def student_report_card_pdf(self, report_id, **kw):
        """Download report card PDF"""
        student = self._get_student()
        
        report_card = request.env['school.report.card'].browse(report_id)
        
        # Security check
        if report_card.student_id.id != student.id:
            raise AccessError("You can only download your own report cards")
        
        # Generate PDF using Odoo's standard method
        pdf_content = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'school_academic.action_report_report_card',
            report_card.ids
        )[0]
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', f'attachment; filename="Report_Card_{report_card.name}.pdf"')
        ]
        
        return request.make_response(pdf_content, headers=pdfhttpheaders)

    @http.route(['/my/student/fees'], type='http', auth='user', website=True)
    def student_fees(self, **kw):
        """Student fees page"""
        student = self._get_student()
        
        # Get fee records
        fees = request.env['school.student.fee'].search([
            ('student_id', '=', student.id)
        ], order='due_date desc')
        
        # Calculate totals
        total_amount = sum(fees.mapped('amount_total'))
        total_paid = sum(fees.mapped('amount_paid'))
        total_due = sum(fees.mapped('amount_due'))
        
        values = {
            'student': student,
            'fees': fees,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_due': total_due,
            'page_name': 'student_fees',
        }
        
        return request.render('school_portal.student_fees', values)

    @http.route(['/my/student/fee/<int:fee_id>/invoice'], type='http', auth='user')
    def student_fee_invoice(self, fee_id, **kw):
        """Download fee invoice PDF"""
        student = self._get_student()
        
        fee = request.env['school.student.fee'].browse(fee_id)
        
        # Security check
        if fee.student_id.id != student.id:
            raise AccessError("You can only download your own invoices")
        
        if not fee.invoice_id:
            return request.redirect('/my/student/fees?error=no_invoice')
        
        # Generate invoice PDF
        pdf_content = request.env['ir.actions.report'].sudo()._render_qweb_pdf(
            'account.account_invoices',
            fee.invoice_id.ids
        )[0]
        
        pdfhttpheaders = [
            ('Content-Type', 'application/pdf'),
            ('Content-Length', len(pdf_content)),
            ('Content-Disposition', f'attachment; filename="Invoice_{fee.invoice_id.name}.pdf"')
        ]
        
        return request.make_response(pdf_content, headers=pdfhttpheaders)
