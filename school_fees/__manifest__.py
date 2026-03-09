{
    "name": "School Fees",
    "version": "18.0.1.0.0",
    "category": "Education",
    "summary": "School Fees Management and Invoicing",
    "depends": ["school_core", "account", "product", "mail", "base_automation"],
    "data": [
        "security/security_groups.xml",
        "security/ir.model.access.csv",
        
        "data/product_data.xml",
        "data/email_templates.xml",
        "data/cron_jobs.xml",
        "data/automation_rules.xml",

        "views/menu.xml",
        "views/fee_structure_views.xml",
        "views/scholarship_views.xml",
        "views/student_fee_views.xml",
        "views/wizard_views.xml",

        "report/fee_statement_report.xml",
        "report/fee_statement_template.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
