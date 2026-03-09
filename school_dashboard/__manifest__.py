{
    "name": "School Dashboard",
    "version": "18.0.1.0.0",
    "category": "Education",
    "summary": "Comprehensive Analytics Dashboard for School Management",
    "description": """
        School Dashboard Module
        =======================
        
        Features:
        ---------
        * Student Analytics Dashboard
        * Fee Collection Analytics
        * Academic Performance Dashboard
        * Attendance Analytics
        * Grade-wise Statistics
        * Financial Reports
        * Interactive Charts and Graphs
        * Real-time KPIs
        * Customizable Filters
        * Export Reports
    """,
    "depends": [
        "school_core",
        "school_academic",
        "school_fees",
        "web",
        "board",
    ],
    "data": [
        "security/ir.model.access.csv",
        
        "views/dashboard_views.xml",
        "views/student_analytics_views.xml",
        "views/fee_analytics_views.xml",
        "views/academic_analytics_views.xml",
        "views/menu.xml",
        
        "report/dashboard_reports.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js",
            "school_dashboard/static/src/css/dashboard.css",
            "school_dashboard/static/src/js/dashboard.js",
            "school_dashboard/static/src/xml/dashboard.xml",
        ],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
    "license": "LGPL-3",
}
