from odoo import models, fields, api
from datetime import date

class SchoolStudent(models.Model):
    _name = "school.student"
    _description = "School Student"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    student_code = fields.Char(readonly=True, copy=False, tracking=True)

    photo = fields.Image()

    partner_id = fields.Many2one("res.partner", string="Contact")
    
    # Parent/Guardian relationship
    parent_ids = fields.Many2many(
        "school.parent",
        "school_student_parent_rel",
        "student_id",
        "parent_id",
        string="Parents/Guardians"
    )
    
    parent_count = fields.Integer(
        compute="_compute_parent_count",
        string="Number of Parents"
    )
    
    # Contact fields
    email = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    address = fields.Text()

    gender = fields.Selection([
        ("male", "Male"),
        ("female", "Female"),
    ])

    dob = fields.Date(string="Date of Birth")
    age = fields.Integer(compute="_compute_age", store=True)

    grade_id = fields.Many2one("school.grade", tracking=True)
    section_id = fields.Many2one("school.section", tracking=True)

    admission_date = fields.Date(default=fields.Date.today)

    status = fields.Selection([
        ("draft", "Applicant"),
        ("enrolled", "Enrolled"),
        ("active", "Active"),
        ("graduated", "Graduated"),
        ("dropped", "Dropped"),
    ], default="draft", tracking=True)

    active = fields.Boolean(default=True)

    academic_year_id = fields.Many2one("school.academic.year")

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )

    @api.depends("dob")
    def _compute_age(self):
        for rec in self:
            if rec.dob:
                today = date.today()
                rec.age = today.year - rec.dob.year - (
                    (today.month, today.day) < (rec.dob.month, rec.dob.day)
                )
            else:
                rec.age = 0
    
    @api.depends("parent_ids")
    def _compute_parent_count(self):
        for rec in self:
            rec.parent_count = len(rec.parent_ids)
    
    def action_view_parents(self):
        """Open list of parents/guardians"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parents/Guardians',
            'res_model': 'school.parent',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.parent_ids.ids)],
            'context': {'default_student_ids': [(4, self.id)]},
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("student_code"):
                vals["student_code"] = self.env["ir.sequence"].next_by_code("school.student") or "NEW"
        return super().create(vals_list)
