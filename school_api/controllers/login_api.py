from odoo import http
from odoo.http import request

class SchoolAuthAPI(http.Controller):

    @http.route('/api/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def api_login(self, **kwargs):
        # 1. Get credentials from params
        db = kwargs.get('db')  # Database name
        login = kwargs.get('login')  # Username/Email
        password = kwargs.get('password')

        if not login or not password:
            return {'error': 'Missing credentials', 'code': 400}

        try:
            # 2. Use provided db or get from request context
            database = db or request.session.db or request.db
            
            if not database:
                return {'error': 'Database not specified', 'code': 400}
            
            # 3. Authenticate using the correct credential format
            credential = {
                'type': 'password',
                'login': login,
                'password': password
            }
            
            auth_info = request.session.authenticate(database, credential)
            uid = auth_info.get('uid')
            
            if not uid:
                return {'error': 'Authentication failed', 'code': 401}

            # 3. Fetch user/student info to return to the app
            user = request.env['res.users'].sudo().browse(uid)
            
            # Link to our school student model if applicable
            # (Assuming you added a partner_id or user_id link in your student model)
            student = request.env['school.student'].sudo().search([
                ('partner_id', '=', user.partner_id.id)
            ], limit=1)

            return {
                'status': 'success',
                'session_id': request.session.sid, # The Token for the app
                'uid': uid,
                'name': user.name,
                'is_student': bool(student),
                'student_id': student.id if student else False,
                'company_name': user.company_id.name
            }

        except Exception as e:
            return {'error': str(e), 'code': 500}

    @http.route('/api/auth/logout', type='json', auth='user', methods=['POST'])
    def api_logout(self):
        request.session.logout()
        return {'status': 'success', 'message': 'Logged out'}