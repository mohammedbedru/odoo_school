from odoo import models, fields

class SchoolTeacher(models.Model):
    _name = "school.teacher"
    _description = "School Teacher"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)

    employee_id = fields.Many2one("hr.employee", tracking=True)
    partner_id = fields.Many2one("res.partner")

    phone = fields.Char()
    email = fields.Char()

    active = fields.Boolean(default=True)

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )
