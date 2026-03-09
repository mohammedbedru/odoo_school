# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class BulkGradeReportWizard(models.TransientModel):
    _name = "school.bulk.grade.report.wizard"
    _description = "Bulk Grade Report Wizard"

    academic_year_id = fields.Many2one(
        "school.academic.year",
        string="Academic Year",
        required=True
    )
    
    grade_id = fields.Many2one(
        "school.grade",
        string="Grade",
        required=True
    )
    
    section_id = fields.Many2one(
        "school.section",
        string="Section",
        required=True,
        domain="[('grade_id', '=', grade_id)]"
    )
    
    term = fields.Selection([
        ("t1", "Term 1"),
        ("t2", "Term 2"),
        ("t3", "Term 3"),
    ], string="Term", required=True, default="t1")
    
    subject_ids = fields.Many2many(
        "school.subject",
        string="Subjects",
        required=True,
        domain="[('grade_id', '=', grade_id)]",
        help="Select subjects to include in the report"
    )

    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        """Clear section and subjects when grade changes"""
        self.section_id = False
        self.subject_ids = False
        
        if self.grade_id:
            return {
                'domain': {
                    'section_id': [('grade_id', '=', self.grade_id.id)],
                    'subject_ids': [('grade_id', '=', self.grade_id.id)]
                }
            }
        return {
            'domain': {
                'section_id': [],
                'subject_ids': []
            }
        }

    def action_print_report(self):
        """Generate the bulk grade report PDF"""
        self.ensure_one()
        
        # Get all students in the section
        students = self.env['school.student'].search([
            ('grade_id', '=', self.grade_id.id),
            ('section_id', '=', self.section_id.id),
            ('status', 'in', ['active', 'enrolled'])
        ], order='name')
        
        if not students:
            raise ValidationError("No students found in the selected section!")
        
        if not self.subject_ids:
            raise ValidationError("Please select at least one subject!")
        
        # Return report action directly with the wizard record
        return self.env.ref('school_academic.action_report_bulk_grades').report_action(self)
