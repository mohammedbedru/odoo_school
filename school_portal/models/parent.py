from odoo import models, fields, api
from odoo.exceptions import UserError
import secrets
import string


class SchoolParent(models.Model):
    _inherit = "school.parent"

    user_id = fields.Many2one(
        "res.users",
        string="Portal User",
        help="Portal user account for this parent",
        domain=[('share', '=', True)]
    )

    def _generate_password(self, length=12):
        """Generate a random secure password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%"
        password = ''.join(secrets.choice(alphabet) for i in range(length))
        return password

    def action_grant_portal_access(self):
        """Create portal user for parent"""
        self.ensure_one()
        
        if self.user_id:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': 'Parent already has portal access',
                    'type': 'warning',
                    'sticky': False,
                }
            }
        
        if not self.email:
            raise UserError('Parent must have an email address to grant portal access.')
        
        # Generate random password
        password = self._generate_password()
        
        # Create portal user
        portal_group = self.env.ref('school_portal.group_portal_parent')
        user = self.env['res.users'].with_context(no_reset_password=True).create({
            'name': self.name,
            'login': self.email,
            'email': self.email,
            'password': password,
            'groups_id': [(6, 0, [portal_group.id])],
            'partner_id': self.partner_id.id if self.partner_id else False,
        })
        
        self.user_id = user.id
        
        # Send password reset email
        try:
            user.action_reset_password()
            message = f'Portal access granted. Password reset email sent to {self.email}'
        except Exception as e:
            message = f'Portal access granted. Login: {user.login} | Temporary Password: {password}'
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': True,
            }
        }

    def action_revoke_portal_access(self):
        """Remove portal access"""
        self.ensure_one()
        if self.user_id:
            self.user_id.active = False
            self.user_id = False
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': 'Portal access revoked',
                'type': 'info',
                'sticky': False,
            }
        }
