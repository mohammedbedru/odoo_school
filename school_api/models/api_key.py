from odoo import models, fields, api
import secrets
import string


class SchoolAPIKey(models.Model):
    _name = 'school.api.key'
    _description = 'API Key Management'
    _order = 'create_date desc'
    
    name = fields.Char('Key Name', required=True, help='Descriptive name for this API key')
    key = fields.Char('API Key', readonly=False, copy=False, index=True,required=False)
    active = fields.Boolean('Active', default=True)
    description = fields.Text('Description')
    
    # Usage tracking
    usage_count = fields.Integer('Usage Count', default=0, readonly=True)
    last_used = fields.Datetime('Last Used', readonly=True)
    
    # Permissions (future enhancement)
    allowed_endpoints = fields.Text('Allowed Endpoints', help='Comma-separated list of allowed endpoints')
    
    _sql_constraints = [
        ('key_unique', 'unique(key)', 'API Key must be unique!')
    ]
    
    # The default_get method is more reliable than using default= in the field definition for complex scenarios like this.
    @api.model
    def default_get(self, fields_list):
        """Set default values including auto-generated key"""
        defaults = super(SchoolAPIKey, self).default_get(fields_list)
        if 'key' in fields_list:
            defaults['key'] = self._generate_api_key()
        return defaults
    
    @api.model_create_multi
    def create(self, vals_list):
        """Generate API key on creation if not provided"""
        for vals in vals_list:
            if 'key' not in vals or not vals.get('key'):
                vals['key'] = self._generate_api_key()
        return super(SchoolAPIKey, self).create(vals_list)
    
    def _generate_api_key(self):
        """Generate a secure random API key"""
        alphabet = string.ascii_letters + string.digits
        return 'sk_' + ''.join(secrets.choice(alphabet) for _ in range(48))
    
    def action_regenerate_key(self):
        """Regenerate API key"""
        for record in self:
            record.key = self._generate_api_key()
            record.usage_count = 0
            record.last_used = False
        return True
    
    def action_deactivate(self):
        """Deactivate API key"""
        self.write({'active': False})
        return True
