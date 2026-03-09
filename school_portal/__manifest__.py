{
    "name": "School Portal",
    "version": "18.0.1.0.0",
    "category": "Education",
    "summary": "Student and Parent Portal for School Management",
    "description": """
        School Portal Module
        ====================
        
        Features:
        ---------
        * Student Portal with Profile, Timetable, Attendance, Marks, Report Cards
        * Parent Portal to view children's academic records
        * Secure access with strict record rules
        * Download report cards and fee invoices
        * View announcements and upcoming exams
        * Attendance tracking and statistics
        * Fee status and payment history
        * Responsive design for mobile and desktop
    """,
    "depends": [
        "portal",
        "school_core",
        "school_academic",
        "school_fees",
    ],
    "data": [
        "security/portal_security.xml",
        "security/ir.model.access.csv",
        
        "views/portal_templates.xml",
        "views/student_portal_templates.xml",
        "views/parent_portal_templates.xml",
        "views/portal_menu.xml",
        "views/student_views.xml",
        "views/parent_views.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "school_portal/static/src/css/portal.css",
            "school_portal/static/src/js/portal.js",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
