{
    'name': 'School API',
    'version': '1.0.0',
    'category': 'Education',
    'summary': 'REST API for third-party integration with school system',
    'description': """
        School API Module
        ==================
        Provides REST API endpoints for external applications to integrate with the school system.
        
        Features:
        - Student profile API
        - Fee information API
        - Attendance API
        - Grade/Report card API
        - Secure API key authentication
    """,
    'author': 'Your School',
    'depends': ['school_core', 'school_fees', 'school_academic'],
    'data': [
        'security/ir.model.access.csv',
        # 'views/api_key_views.xml',
    ],
    # 'assets': {
    #     'web.assets_backend': [
    #         'school_api/static/src/js/password_field.js',
    #         'school_api/static/src/xml/password_field.xml',
    #     ],
    # },
    'installable': True,
    'application': False,
    'auto_install': False,
}
