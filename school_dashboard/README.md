# School Dashboard Module

Comprehensive analytics and dashboard module for school management system.

## Features

### 1. Main Dashboard
- **Real-time KPIs**: Student count, fee collection, attendance rates
- **Visual Cards**: Interactive cards with key metrics
- **Quick Actions**: Direct links to important views
- **Progress Bars**: Visual representation of collection and attendance rates

### 2. Student Analytics
- **Student Distribution**: By grade, section, and status
- **Gender Distribution**: Male/female ratio analysis
- **Age Analytics**: Average age by grade
- **Grade-wise Analytics**: Comprehensive metrics per grade
  - Student count
  - Attendance rates
  - Academic performance
  - Fee collection status

### 3. Fee Analytics
- **Fee Collection Overview**: Total, collected, pending, overdue
- **Collection Rate**: Percentage of fees collected
- **Monthly Collection Trends**: Track collection over time
- **Grade-wise Collection**: Fee analysis by grade
- **Fee Defaulters Report**:
  - List of students with overdue fees
  - Days overdue tracking
  - Contact information
  - Send reminder functionality

### 4. Academic Analytics
- **Performance Metrics**:
  - Average percentage by grade/section
  - Pass percentage
  - Grade distribution (A, B, C, D, F)
- **Subject Performance**:
  - Average marks per subject
  - Highest/lowest marks
  - Pass/fail analysis
- **Attendance Analytics**:
  - Daily attendance rates
  - Present/absent/late counts
  - Trend analysis

### 5. Visualization
- **Graph Views**: Bar, line, pie charts
- **Pivot Tables**: Multi-dimensional analysis
- **Interactive Dashboards**: Drill-down capabilities

## Installation

1. Copy module to `custom_addons` directory
2. Update apps list
3. Install "School Dashboard" module

## Dependencies

- school_core
- school_academic
- school_fees
- web
- board

## Usage

### Accessing Dashboard

Navigate to: **School → Dashboard → Main Dashboard**

### Student Analytics

**School → Dashboard → Student Analytics**
- Student Distribution: View by grade/section
- Grade Analytics: Detailed grade-wise metrics

### Fee Analytics

**School → Dashboard → Fee Analytics**
- Fee Collection: Overall collection analysis
- Monthly Collection: Month-by-month trends
- Fee Defaulters: Overdue payments tracking

### Academic Analytics

**School → Dashboard → Academic Analytics**
- Performance Analytics: Grade distribution and averages
- Subject Performance: Subject-wise analysis
- Attendance Analytics: Attendance trends

## Models

### school.dashboard
Main dashboard model with computed KPIs

### school.student.analytics
SQL view for student distribution analysis

### school.grade.analytics
Grade-wise comprehensive analytics

### school.fee.analytics
SQL view for fee collection analysis

### school.monthly.fee.collection
Monthly fee collection tracking

### school.fee.defaulter
Fee defaulter tracking and management

### school.academic.analytics
Academic performance analytics

### school.subject.performance
Subject-wise performance tracking

### school.attendance.analytics
SQL view for attendance analysis

## Views

### Dashboard Views
- Kanban view with interactive cards
- Form view with detailed statistics
- Quick action buttons

### Analytics Views
- List views for data tables
- Graph views for visualizations
- Pivot views for multi-dimensional analysis

## Reports

### Dashboard Summary Report
PDF report with all key metrics:
- Student statistics
- Fee collection summary
- Academic performance
- Staff information

## Customization

### Adding Custom Metrics

1. Extend `school.dashboard` model
2. Add computed fields
3. Update dashboard views

### Custom Charts

1. Create new graph views
2. Define measure fields
3. Add to menu structure

### Custom Reports

1. Create report template
2. Define report action
3. Add to model

## Security

Access rights defined for:
- Admin: Full access
- Manager: Read access
- Teacher: Limited read access

## Performance

- SQL views for efficient queries
- Computed fields with proper dependencies
- Indexed fields for fast lookups

## Troubleshooting

### Dashboard Not Loading
- Check module dependencies
- Verify data exists in related models
- Check user permissions

### Incorrect Statistics
- Refresh computed fields
- Check date filters
- Verify data integrity

### Slow Performance
- Check database indexes
- Optimize SQL views
- Review computed field dependencies

## Future Enhancements

- Real-time updates with websockets
- Export to Excel functionality
- Email scheduled reports
- Mobile-responsive dashboard
- Custom dashboard builder
- Predictive analytics
- Comparison with previous years
- Goal tracking and alerts

## Support

For issues or questions:
1. Check documentation
2. Review model code
3. Check Odoo logs

## Version History

### 1.0.0 (2026-02-10)
- Initial release
- Main dashboard with KPIs
- Student analytics
- Fee analytics
- Academic analytics
- Multiple visualization options

## License

LGPL-3

## Credits

Developed for Odoo 18.0 school management system.
