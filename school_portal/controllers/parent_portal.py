from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError


class ParentPortalController(http.Controller):

    def _get_parent(self):
        """Get current parent or raise error"""
        parent = request.env['school.parent'].search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        if not parent:
            raise AccessError("You are not registered as a parent")
        
        return parent

    def _get_child(self, child_id, parent):
        """Get child and verify parent relationship"""
        child = request.env['school.student'].browse(child_id)
        
        if parent.id not in child.parent_ids.ids:
            raise AccessError("You can only view your own children's records")
        
        return child

    @http.route(['/my/parent/children'], type='http', auth='user', website=True)
    def parent_children(self, **kw):
        """Parent's children list"""
        parent = self._get_parent()
        
        # Get all children
        children = request.env['school.student'].search([
            ('parent_ids', 'in', [parent.id])
        ])
        
        values = {
            'parent': parent,
            'children': children,
            'page_name': 'parent_children',
        }
        
        return request.render('school_portal.parent_children', values)

    @http.route(['/my/parent/child/<int:child_id>/dashboard'], type='http', auth='user', website=True)
    def parent_child_dashboard(self, child_id, **kw):
        """Child's dashboard for parent"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        # Get latest report card
        latest_report = request.env['school.report.card'].search([
            ('student_id', '=', child.id),
            ('state', '=', 'published')
        ], order='academic_year_id desc, term desc', limit=1)
        
        # Calculate attendance percentage
        attendance_lines = request.env['school.attendance.line'].search([
            ('student_id', '=', child.id)
        ])
        
        if attendance_lines:
            present_count = len(attendance_lines.filtered(lambda a: a.status == 'present'))
            attendance_percentage = (present_count / len(attendance_lines)) * 100
        else:
            attendance_percentage = 0
        
        # Get upcoming exams
        upcoming_exams = request.env['school.exam'].sudo().search([
            ('section_id', '=', child.section_id.id),
            ('date', '>=', request.env.cr.now())
        ], order='date asc', limit=5)
        
        values = {
            'parent': parent,
            'child': child,
            'latest_report': latest_report,
            'gpa': latest_report.average if latest_report else 0,
            'attendance_percentage': round(attendance_percentage, 2),
            'upcoming_exams': upcoming_exams,
            'page_name': 'parent_child_dashboard',
        }
        
        return request.render('school_portal.parent_child_dashboard', values)

    @http.route(['/my/parent/child/<int:child_id>/attendance'], type='http', auth='user', website=True)
    def parent_child_attendance(self, child_id, **kw):
        """Child's attendance for parent"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        # Get attendance records
        attendance_lines = request.env['school.attendance.line'].search([
            ('student_id', '=', child.id)
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
            'parent': parent,
            'child': child,
            'attendance_lines': attendance_lines,
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'attendance_percentage': round(attendance_percentage, 2),
            'page_name': 'parent_child_attendance',
        }
        
        return request.render('school_portal.parent_child_attendance', values)

    @http.route(['/my/parent/child/<int:child_id>/marks'], type='http', auth='user', website=True)
    def parent_child_marks(self, child_id, **kw):
        """Child's exam marks for parent"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        # Get exam marks
        exam_marks = request.env['school.exam.mark'].search([
            ('student_id', '=', child.id)
        ], order='id desc')
        
        # Sort by exam date in Python
        exam_marks = exam_marks.sorted(lambda l: l.exam_id.date, reverse=True)
        
        
        values = {
            'parent': parent,
            'child': child,
            'exam_marks': exam_marks,
            'page_name': 'parent_child_marks',
        }
        
        return request.render('school_portal.parent_child_marks', values)

    @http.route(['/my/parent/child/<int:child_id>/report-cards'], type='http', auth='user', website=True)
    def parent_child_report_cards(self, child_id, **kw):
        """Child's report cards for parent"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        # Get published report cards
        report_cards = request.env['school.report.card'].search([
            ('student_id', '=', child.id),
            ('state', '=', 'published')
        ], order='academic_year_id desc, term desc')
        
        values = {
            'parent': parent,
            'child': child,
            'report_cards': report_cards,
            'page_name': 'parent_child_report_cards',
        }
        
        return request.render('school_portal.parent_child_report_cards', values)

    @http.route(['/my/parent/child/<int:child_id>/report-card/<int:report_id>'], type='http', auth='user', website=True)
    def parent_child_report_card_detail(self, child_id, report_id, **kw):
        """Child's report card detail for parent"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        report_card = request.env['school.report.card'].browse(report_id)
        
        # Security check
        if report_card.student_id.id != child.id:
            raise AccessError("Invalid report card")
        
        values = {
            'parent': parent,
            'child': child,
            'report_card': report_card,
            'page_name': 'parent_child_report_cards',
        }
        
        return request.render('school_portal.parent_child_report_card_detail', values)

    @http.route(['/my/parent/child/<int:child_id>/report-card/<int:report_id>/pdf'], type='http', auth='user')
    def parent_child_report_card_pdf(self, child_id, report_id, **kw):
        """Download child's report card PDF"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        report_card = request.env['school.report.card'].browse(report_id)
        
        # Security check
        if report_card.student_id.id != child.id:
            raise AccessError("Invalid report card")
        

        # Generate PDF
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

    @http.route(['/my/parent/child/<int:child_id>/fees'], type='http', auth='user', website=True)
    def parent_child_fees(self, child_id, **kw):
        """Child's fees for parent"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        # Get fee records
        fees = request.env['school.student.fee'].search([
            ('student_id', '=', child.id)
        ], order='due_date desc')
        
        # Calculate totals
        total_amount = sum(fees.mapped('amount_total'))
        total_paid = sum(fees.mapped('amount_paid'))
        total_due = sum(fees.mapped('amount_due'))
        
        values = {
            'parent': parent,
            'child': child,
            'fees': fees,
            'total_amount': total_amount,
            'total_paid': total_paid,
            'total_due': total_due,
            'page_name': 'parent_child_fees',
        }
        
        return request.render('school_portal.parent_child_fees', values)

    @http.route(['/my/parent/child/<int:child_id>/fee/<int:fee_id>/invoice'], type='http', auth='user')
    def parent_child_fee_invoice(self, child_id, fee_id, **kw):
        """Download child's fee invoice PDF"""
        parent = self._get_parent()
        child = self._get_child(child_id, parent)
        
        fee = request.env['school.student.fee'].browse(fee_id)
        
        # Security check
        if fee.student_id.id != child.id:
            raise AccessError("Invalid fee record")
        
        if not fee.invoice_id:
            return request.redirect(f'/my/parent/child/{child_id}/fees?error=no_invoice')
        
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
