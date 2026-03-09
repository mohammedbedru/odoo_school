{
    "name": "School Academic",
    "version": "18.0.1.0.0",
    "category": "Education",
    "summary": "Academic Operations: Timetable, Attendance, Exams, Report Cards",
    "depends": ["school_core"],
    "data": [
        "security/ir.model.access.csv",

        "report/attendance_sheet_report.xml",
        "report/attendance_sheet_template.xml",

        "report/report_card_report.xml",
        "report/report_card_template.xml",

        "report/bulk_grade_report.xml",

        "views/academic_menu.xml",
        "views/timetable_views.xml",
        "views/attendance_views.xml",
        "views/exam_views.xml",
        "views/report_card_views.xml",

        "wizard/attendance_sheet_wizard_views.xml",
        "wizard/promotion_wizard_views.xml",
        "wizard/bulk_grade_report_wizard_views.xml",


    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
