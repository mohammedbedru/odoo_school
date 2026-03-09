from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.exceptions import AccessError
import logging

_logger = logging.getLogger(__name__)


class SchoolPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        """Add school-specific counters to portal home"""
        values = super()._prepare_home_portal_values(counters)
        
        user = request.env.user
        
        # Initialize flags
        values['is_student'] = False
        values['is_parent'] = False
        
        _logger.info(f"Portal home accessed by user: {user.name} (ID: {user.id})")
        
        # Check if user is a student
        student = request.env['school.student'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)
        
        # Check if user is a parent
        parent = request.env['school.parent'].sudo().search([
            ('user_id', '=', user.id)
        ], limit=1)
        
        if student:
            values['is_student'] = True
            values['student'] = student
            _logger.info(f"User is student: {student.name}")
            
            # Always provide count for menu display
            values['report_card_count'] = request.env['school.report.card'].search_count([
                ('student_id', '=', student.id),
                ('state', '=', 'published')
            ])
            _logger.info(f"Report card count: {values['report_card_count']}")
        
        if parent:
            values['is_parent'] = True
            values['parent'] = parent
            _logger.info(f"User is parent: {parent.name}")
            
            # Get children
            children = request.env['school.student'].sudo().search([
                ('parent_ids', 'in', [parent.id])
            ])
            values['children'] = children
            values['children_count'] = len(children)
            _logger.info(f"Children count: {values['children_count']}")
        
        _logger.info(f"Portal values: is_student={values['is_student']}, is_parent={values['is_parent']}")
        
        return values

    @http.route(['/my/school'], type='http', auth='user', website=True)
    def portal_my_school(self, **kw):
        """School portal home page"""
        values = self._prepare_home_portal_values(['report_card_count', 'exam_count', 'fee_count'])
        values['page_name'] = 'school_portal_home'
        return request.render('school_portal.portal_my_school', values)
