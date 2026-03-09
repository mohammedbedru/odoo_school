# School Dashboard - Installation Guide

## Prerequisites

Before installing the School Dashboard module, ensure you have:

1. ✅ Odoo 18.0 installed and running
2. ✅ `school_core` module installed
3. ✅ `school_academic` module installed
4. ✅ `school_fees` module installed
5. ✅ Database with school data (students, fees, exams, etc.)

## Installation Steps

### Step 1: Copy Module Files

```bash
# Navigate to Odoo custom addons directory
cd /path/to/odoo/custom_addons

# Ensure school_dashboard directory exists with all files
ls school_dashboard/
```

Expected structure:
```
school_dashboard/
├── __init__.py
├── __manifest__.py
├── README.md
├── models/
│   ├── __init__.py
│   ├── dashboard.py
│   ├── student_analytics.py
│   ├── fee_analytics.py
│   └── academic_analytics.py
├── views/
│   ├── dashboard_views.xml
│   ├── student_analytics_views.xml
│   ├── fee_analytics_views.xml
│   ├── academic_analytics_views.xml
│   └── menu.xml
├── security/
│   └── ir.model.access.csv
├── static/
│   └── src/
│       ├── css/
│       │   └── dashboard.css
│       ├── js/
│       │   └── dashboard.js
│       └── xml/
│           └── dashboard.xml
├── report/
│   └── dashboard_reports.xml
└── data/
```

### Step 2: Update Apps List

1. Open Odoo in browser
2. Go to **Apps** menu
3. Click **Update Apps List** button
4. Confirm the update

### Step 3: Install Module

1. In **Apps** menu, search for "School Dashboard"
2. Click **Install** button
3. Wait for installation to complete

### Step 4: Verify Installation

1. Go to **School** menu
2. You should see **Dashboard** submenu
3. Click **Dashboard → Main Dashboard**
4. Verify dashboard loads with data

## Post-Installation Configuration

### 1. Generate Initial Analytics Data

Some analytics models need initial data generation:

```python
# Run in Odoo shell or create a script

# Generate grade analytics
env['school.grade.analytics'].search([]).unlink()  # Clear old data
grades = env['school.grade'].search([])
years = env['school.academic.year'].search([])

for grade in grades:
    for year in years:
        env['school.grade.analytics'].create({
            'grade_id': grade.id,
            'academic_year_id': year.id,
        })

# Generate academic analytics
env['school.academic.analytics'].search([]).unlink()
for year in years:
    for term in ['t1', 't2', 't3']:
        for grade in grades:
            env['school.academic.analytics'].create({
                'academic_year_id': year.id,
                'term': term,
                'grade_id': grade.id,
            })

# Generate monthly fee collection records
env['school.monthly.fee.collection'].search([]).unlink()
for month in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']:
    env['school.monthly.fee.collection'].create({
        'month': month,
        'year': '2024',
    })

# Generate fee defaulter records
students = env['school.student'].search([('status', 'in', ['enrolled', 'active'])])
env['school.fee.defaulter'].search([]).unlink()
for student in students:
    overdue_fees = env['school.student.fee'].search([
        ('student_id', '=', student.id),
        ('is_overdue', '=', True)
    ])
    if overdue_fees:
        env['school.fee.defaulter'].create({
            'student_id': student.id,
        })

# Generate subject performance records
subjects = env['school.subject'].search([])
env['school.subject.performance'].search([]).unlink()
for year in years:
    for term in ['t1', 't2', 't3']:
        for subject in subjects:
            for grade in grades:
                env['school.subject.performance'].create({
                    'subject_id': subject.id,
                    'academic_year_id': year.id,
                    'term': term,
                    'grade_id': grade.id,
                })
```

### 2. Set User Permissions

Ensure users have appropriate access:

1. Go to **Settings → Users & Companies → Users**
2. Edit user
3. Add to appropriate groups:
   - **School Admin**: Full dashboard access
   - **School Manager**: Read-only dashboard access
   - **School Teacher**: Limited analytics access

### 3. Configure Dashboard Preferences

No additional configuration needed - dashboard uses existing data.

## Verification Checklist

After installation, verify:

- [ ] Dashboard menu appears under School
- [ ] Main Dashboard loads without errors
- [ ] Student Analytics shows data
- [ ] Fee Analytics displays collection data
- [ ] Academic Analytics shows performance data
- [ ] Graphs and charts render correctly
- [ ] Pivot tables work
- [ ] PDF reports generate successfully
- [ ] No errors in Odoo logs

## Troubleshooting

### Issue: Dashboard Shows Zero Values

**Solution:**
- Ensure you have data in related models (students, fees, exams)
- Run data generation scripts above
- Refresh browser cache

### Issue: SQL View Errors

**Solution:**
```sql
-- Manually create views if needed
-- Connect to PostgreSQL database

-- Student Analytics View
CREATE OR REPLACE VIEW school_student_analytics AS (
    SELECT
        ROW_NUMBER() OVER() as id,
        grade_id,
        section_id,
        status,
        COUNT(*) as student_count,
        SUM(CASE WHEN gender = 'male' THEN 1 ELSE 0 END) as male_count,
        SUM(CASE WHEN gender = 'female' THEN 1 ELSE 0 END) as female_count,
        AVG(age) as average_age
    FROM school_student
    WHERE active = true
    GROUP BY grade_id, section_id, status
);

-- Fee Analytics View
CREATE OR REPLACE VIEW school_fee_analytics AS (
    SELECT
        ROW_NUMBER() OVER() as id,
        sf.academic_year_id,
        sf.term,
        s.grade_id,
        sf.currency_id,
        COUNT(DISTINCT sf.student_id) as student_count,
        SUM(sf.amount_total + sf.amount_paid) as total_amount,
        SUM(sf.amount_paid) as collected_amount,
        SUM(sf.amount_due) as pending_amount,
        SUM(CASE WHEN sf.is_overdue = true THEN sf.amount_due ELSE 0 END) as overdue_amount,
        SUM(CASE WHEN sf.payment_state = 'paid' THEN 1 ELSE 0 END) as paid_count,
        SUM(CASE WHEN sf.payment_state != 'paid' THEN 1 ELSE 0 END) as pending_count,
        SUM(CASE WHEN sf.is_overdue = true THEN 1 ELSE 0 END) as overdue_count,
        CASE 
            WHEN SUM(sf.amount_total + sf.amount_paid) > 0 
            THEN (SUM(sf.amount_paid) / SUM(sf.amount_total + sf.amount_paid) * 100)
            ELSE 0 
        END as collection_rate
    FROM school_student_fee sf
    JOIN school_student s ON s.id = sf.student_id
    GROUP BY sf.academic_year_id, sf.term, s.grade_id, sf.currency_id
);

-- Attendance Analytics View
CREATE OR REPLACE VIEW school_attendance_analytics AS (
    SELECT
        ROW_NUMBER() OVER() as id,
        s.grade_id,
        s.section_id,
        a.attendance_date,
        COUNT(DISTINCT a.student_id) as total_students,
        SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) as present_count,
        SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) as absent_count,
        SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) as late_count,
        CASE 
            WHEN COUNT(*) > 0 
            THEN (SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)::float / COUNT(*) * 100)
            ELSE 0 
        END as attendance_rate
    FROM school_attendance a
    JOIN school_student s ON s.id = a.student_id
    WHERE a.attendance_date IS NOT NULL
    GROUP BY s.grade_id, s.section_id, a.attendance_date
);
```

### Issue: Permission Denied

**Solution:**
- Check user is in appropriate security group
- Verify `ir.model.access.csv` is loaded
- Update module to reload security rules

### Issue: Charts Not Displaying

**Solution:**
- Clear browser cache
- Check JavaScript console for errors
- Verify static files are loaded
- Restart Odoo server

### Issue: Slow Performance

**Solution:**
```sql
-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_student_grade ON school_student(grade_id);
CREATE INDEX IF NOT EXISTS idx_student_section ON school_student(section_id);
CREATE INDEX IF NOT EXISTS idx_student_status ON school_student(status);
CREATE INDEX IF NOT EXISTS idx_fee_student ON school_student_fee(student_id);
CREATE INDEX IF NOT EXISTS idx_fee_year ON school_student_fee(academic_year_id);
CREATE INDEX IF NOT EXISTS idx_fee_overdue ON school_student_fee(is_overdue);
CREATE INDEX IF NOT EXISTS idx_attendance_student ON school_attendance(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_date ON school_attendance(attendance_date);
```

## Upgrade Instructions

If upgrading from a previous version:

```bash
# Backup database first!
pg_dump your_database > backup_before_dashboard_upgrade.sql

# Upgrade module
./odoo-bin -u school_dashboard -d your_database

# Verify upgrade
# Check Odoo logs for any errors
# Test dashboard functionality
```

## Uninstallation

To uninstall (not recommended):

1. Go to **Apps** menu
2. Search for "School Dashboard"
3. Click **Uninstall**
4. Confirm uninstallation

**Note:** This will remove all dashboard data and views.

## Support

If you encounter issues:

1. Check Odoo logs: `/var/log/odoo/odoo-server.log`
2. Enable debug mode: Add `?debug=1` to URL
3. Check PostgreSQL logs for SQL errors
4. Review module code in `custom_addons/school_dashboard/`

## Next Steps

After successful installation:

1. Explore Main Dashboard
2. Review Student Analytics
3. Check Fee Collection reports
4. Analyze Academic Performance
5. Generate PDF reports
6. Customize views as needed

## Additional Resources

- Odoo Documentation: https://www.odoo.com/documentation/18.0/
- Module README: `custom_addons/school_dashboard/README.md`
- Model Documentation: Check docstrings in Python files

---

**Installation Complete!** 🎉

Your School Dashboard is now ready to use. Navigate to **School → Dashboard** to get started.
