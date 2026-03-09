from odoo import models, fields, api
from odoo.exceptions import ValidationError

class SchoolBulkInvoiceWizard(models.TransientModel):
    _name = "school.bulk.invoice.wizard"
    _description = "Bulk Invoice Generator Wizard"

    academic_year_id = fields.Many2one("school.academic.year", required=True)
    grade_id = fields.Many2one("school.grade", required=True)
    section_id = fields.Many2one(
        "school.section",
        domain="[('grade_id', '=', grade_id)]"
    )

    term = fields.Selection([
        ("t1", "Term 1"),
        ("t2", "Term 2"),
        ("t3", "Term 3"),
    ], required=True, default="t1")

    structure_id = fields.Many2one(
        "school.fee.structure",
        required=True,
        domain="[('grade_id', '=', grade_id), ('academic_year_id', '=', academic_year_id), ('term', '=', term)]"
    )

    @api.onchange('grade_id')
    def _onchange_grade_id(self):
        """Clear section and structure when grade changes"""
        if self.grade_id:
            self.section_id = False
            self.structure_id = False
            return {
                'domain': {
                    'section_id': [('grade_id', '=', self.grade_id.id)],
                    'structure_id': [
                        ('grade_id', '=', self.grade_id.id),
                        ('academic_year_id', '=', self.academic_year_id.id),
                        ('term', '=', self.term)
                    ]
                }
            }
        else:
            self.section_id = False
            self.structure_id = False
            return {
                'domain': {
                    'section_id': [],
                    'structure_id': []
                }
            }

    @api.onchange('academic_year_id', 'term')
    def _onchange_academic_year_term(self):
        """Update structure domain when academic year or term changes"""
        if self.grade_id:
            self.structure_id = False
            return {
                'domain': {
                    'structure_id': [
                        ('grade_id', '=', self.grade_id.id),
                        ('academic_year_id', '=', self.academic_year_id.id),
                        ('term', '=', self.term)
                    ]
                }
            }

    def action_generate_bulk_invoices(self):
        domain = [("grade_id", "=", self.grade_id.id)]
        if self.section_id:
            domain.append(("section_id", "=", self.section_id.id))

        students = self.env["school.student"].search(domain)

        if not students:
            raise ValidationError("No students found in selected grade/section!")

        created = 0
        for student in students:
            fee = self.env["school.student.fee"].search([
                ("student_id", "=", student.id),
                ("academic_year_id", "=", self.academic_year_id.id),
                ("term", "=", self.term),
            ], limit=1)

            if fee:
                continue

            fee = self.env["school.student.fee"].create({
                "student_id": student.id,
                "academic_year_id": self.academic_year_id.id,
                "term": self.term,
                "structure_id": self.structure_id.id,
            })
            fee.action_generate_invoice()
            created += 1

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Invoices Generated",
                "message": f"{created} invoice(s) created successfully.",
                "sticky": False,
            }
        }
