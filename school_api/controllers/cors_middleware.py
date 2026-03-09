from odoo import http
from odoo.http import request


class CORSMiddleware(http.Controller):
    """Middleware to add CORS headers to API responses"""
    
    @staticmethod
    def add_cors_headers(response):
        """Add CORS headers to response"""
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    @http.route([
        '/api/v2/<path:path>',
    ], type='http', auth='none', methods=['OPTIONS'], csrf=False, cors='*')
    def options_handler(self, **kwargs):
        """Handle OPTIONS preflight requests"""
        response = request.make_response('', headers=[
            ('Access-Control-Allow-Origin', 'http://localhost:3000'),
            ('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With'),
            ('Access-Control-Allow-Credentials', 'true'),
            ('Access-Control-Max-Age', '3600'),
        ])
        return response
