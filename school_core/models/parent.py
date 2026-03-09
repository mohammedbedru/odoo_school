from odoo import models, fields, api


class SchoolParent(models.Model):
    _name = "school.parent"
    _description = "School Parent/Guardian"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(required=True, tracking=True)
    
    partner_id = fields.Many2one(
        "res.partner",
        string="Contact",
        help="Related contact/partner record"
    )
    
    relation = fields.Selection([
        ("father", "Father"),
        ("mother", "Mother"),
        ("guardian", "Guardian"),
        ("other", "Other"),
    ], required=True, default="father", tracking=True)
    
    gender = fields.Selection([
        ("male", "Male"),
        ("female", "Female"),
    ])
    
    email = fields.Char(tracking=True)
    phone = fields.Char(tracking=True)
    mobile = fields.Char(tracking=True)
    
    occupation = fields.Char()
    company_name = fields.Char(string="Company")
    
    address = fields.Text()
    
    # Relationship with students
    student_ids = fields.Many2many(
        "school.student",
        "school_student_parent_rel",
        "parent_id",
        "student_id",
        string="Children"
    )
    
    student_count = fields.Integer(
        compute="_compute_student_count",
        string="Number of Children"
    )
    
    # Emergency contact
    is_emergency_contact = fields.Boolean(
        string="Emergency Contact",
        default=True
    )
    
    # Portal access
    user_id = fields.Many2one(
        "res.users",
        string="Portal User",
        help="Portal user account for this parent",
        domain=[('share', '=', True)]
    )
    
    active = fields.Boolean(default=True)
    
    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company
    )
    
    notes = fields.Text()
    
    @api.depends("student_ids")
    def _compute_student_count(self):
        for rec in self:
            rec.student_count = len(rec.student_ids)
    
    def action_view_students(self):
        """Open list of children"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Children',
            'res_model': 'school.student',
            'view_mode': 'list,form',
            'domain': [('id', 'in', self.student_ids.ids)],
            'context': {'default_parent_ids': [(4, self.id)]},
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        """Create partner if email is provided"""
        for vals in vals_list:
            if vals.get('email') and not vals.get('partner_id'):
                partner = self.env['res.partner'].create({
                    'name': vals.get('name'),
                    'email': vals.get('email'),
                    'phone': vals.get('phone'),
                    'mobile': vals.get('mobile'),
                    'is_company': False,
                })
                vals['partner_id'] = partner.id
        
        return super().create(vals_list)
    
    def write(self, vals):
        """Update partner if exists"""
        result = super().write(vals)
        
        for rec in self:
            if rec.partner_id:
                partner_vals = {}
                if 'name' in vals:
                    partner_vals['name'] = vals['name']
                if 'email' in vals:
                    partner_vals['email'] = vals['email']
                if 'phone' in vals:
                    partner_vals['phone'] = vals['phone']
                if 'mobile' in vals:
                    partner_vals['mobile'] = vals['mobile']
                
                if partner_vals:
                    rec.partner_id.write(partner_vals)
        
        return result
