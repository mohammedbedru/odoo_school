from odoo import models, fields, api

class SchoolFeeStructure(models.Model):
    _name = "school.fee.structure"
    _description = "Fee Structure"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)

    grade_id = fields.Many2one("school.grade", required=True, tracking=True)
    academic_year_id = fields.Many2one("school.academic.year", required=True, tracking=True)

    term = fields.Selection([
        ("t1", "Term 1"),
        ("t2", "Term 2"),
        ("t3", "Term 3"),
    ], required=True, default="t1", tracking=True)

    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id
    )

    line_ids = fields.One2many(
        "school.fee.structure.line",
        "structure_id",
        string="Fee Lines"
    )

    total_amount = fields.Monetary(
        compute="_compute_total_amount",
        store=True,
        currency_field="currency_id"
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    @api.depends("line_ids.amount")
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped("amount"))


class SchoolFeeStructureLine(models.Model):
    _name = "school.fee.structure.line"
    _description = "Fee Structure Line"

    structure_id = fields.Many2one("school.fee.structure", required=True, ondelete="cascade")
    product_id = fields.Many2one("product.product", required=True)

    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(
        related="structure_id.currency_id",
        store=True,
        readonly=True
    )
