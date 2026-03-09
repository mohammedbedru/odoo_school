# School Portal Module

Complete student and parent portal for school management system.

## Features

### Student Portal
- ✅ Profile page with personal information
- ✅ Academic dashboard with GPA, rank, and attendance
- ✅ Weekly timetable with subjects, teachers, and rooms
- ✅ Attendance records with statistics
- ✅ Exam marks and grades
- ✅ Report cards with PDF download
- ✅ Fee status and invoice download
- ✅ Upcoming exams list

### Parent Portal
- ✅ View all children
- ✅ Access each child's academic dashboard
- ✅ View attendance records
- ✅ View exam marks and report cards
- ✅ Download report cards as PDF
- ✅ View fee status and download invoices
- ✅ Track academic progress

## Security

### Strict Access Control
- Students can ONLY see their own records
- Parents can ONLY see their children's records
- No access to other students' data
- No access to teacher private notes
- Secure PDF downloads with access verification

### Record Rules
- `rule_student_own_record` - Students see only their profile
- `rule_student_own_attendance` - Students see only their attendance
- `rule_student_own_exam_marks` - Students see only their marks
- `rule_student_own_report_card` - Students see only their report cards
- `rule_student_own_fees` - Students see only their fees
- `rule_parent_children_*` - Parents see only their children's records

## Installation

1. Copy module to `custom_addons/school_portal/`
2. Update apps list in Odoo
3. Install "School Portal" module
4. Grant portal access to students and parents

## Granting Portal Access

### For Students
1. Go to School → Students
2. Open student record
3. Click "Grant Portal Access" button
4. System creates portal user with login credentials
5. Send credentials to student

### For Parents
1. Go to School → Parents
2. Open parent record
3. Click "Grant Portal Access" button
4. System creates portal user with login credentials
5. Send credentials to parent

## Portal URLs

### Student Portal
- `/my/student/profile` - Student profile
- `/my/student/dashboard` - Academic dashboard
- `/my/student/timetable` - Weekly timetable
- `/my/student/attendance` - Attendance records
- `/my/student/marks` - Exam marks
- `/my/student/report-cards` - Report cards list
- `/my/student/report-card/<id>` - Report card detail
- `/my/student/report-card/<id>/pdf` - Download PDF
- `/my/student/fees` - Fee status
- `/my/student/fee/<id>/invoice` - Download invoice

### Parent Portal
- `/my/parent/children` - Children list
- `/my/parent/child/<id>/dashboard` - Child dashboard
- `/my/parent/child/<id>/attendance` - Child attendance
- `/my/parent/child/<id>/marks` - Child marks
- `/my/parent/child/<id>/report-cards` - Child report cards
- `/my/parent/child/<id>/report-card/<rid>` - Report card detail
- `/my/parent/child/<id>/report-card/<rid>/pdf` - Download PDF
- `/my/parent/child/<id>/fees` - Child fees
- `/my/parent/child/<id>/fee/<fid>/invoice` - Download invoice

## Template Files Structure

```
views/
├── portal_templates.xml          # Base portal layout
├── student_portal_templates.xml  # Student portal pages
├── parent_portal_templates.xml   # Parent portal pages
└── portal_menu.xml               # Portal menu items
```

## Customization

### Adding New Pages
1. Create controller method in `controllers/`
2. Create template in `views/`
3. Add menu item in `views/portal_menu.xml`
4. Add security rules if needed

### Styling
Edit `static/src/css/portal.css` to customize:
- Colors and themes
- Card layouts
- Table styles
- Responsive breakpoints

### Adding Announcements
Create announcement model and add to dashboard:
```python
announcements = request.env['school.announcement'].search([
    ('target', 'in', ['all', 'students']),
    ('active', '=', True)
], order='date desc', limit=5)
```

## Dependencies

- `portal` - Odoo portal module
- `school_core` - School core module
- `school_academic` - Academic management
- `school_fees` - Fee management

## Technical Details

### Models Extended
- `school.student` - Added `user_id` field for portal access
- `school.parent` - Added `user_id` field for portal access

### Security Groups
- `group_portal_student` - Portal access for students
- `group_portal_parent` - Portal access for parents

### Controllers
- `SchoolPortal` - Main portal controller
- `StudentPortalController` - Student-specific pages
- `ParentPortalController` - Parent-specific pages

## Best Practices

1. **Always verify user identity** before showing data
2. **Use record rules** for automatic security
3. **Check parent-child relationship** in parent portal
4. **Log portal access** for security auditing
5. **Use HTTPS** in production for secure login
6. **Implement password policies** for portal users
7. **Send welcome emails** with login instructions
8. **Provide password reset** functionality

## Troubleshooting

### Student Can't Login
- Check if portal access was granted
- Verify user_id field is set on student record
- Check if user is in `group_portal_student` group
- Verify user is active

### Parent Can't See Children
- Check parent_ids on student records
- Verify parent-student relationship exists
- Check record rules are active
- Verify user is in `group_portal_parent` group

### PDF Download Fails
- Check if report card is published
- Verify PDF report is configured
- Check file permissions
- Verify invoice exists for fee

### No Data Showing
- Check if records exist in database
- Verify record rules allow access
- Check if data is published/active
- Review Odoo logs for errors

## Future Enhancements

- [ ] Mobile app integration
- [ ] Push notifications for announcements
- [ ] Online fee payment gateway
- [ ] Chat with teachers
- [ ] Assignment submission
- [ ] Grade comparison charts
- [ ] Attendance leave requests
- [ ] Parent-teacher meeting scheduler
- [ ] Progress reports with graphs
- [ ] Multi-language support

## Support

For issues or questions:
1. Check Odoo logs for errors
2. Review security rules and access rights
3. Verify module dependencies are installed
4. Check portal user configuration

## License

LGPL-3
