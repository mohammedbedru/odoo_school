# OWL Dashboard - User Guide

## Overview

The new School Dashboard is built with modern OWL (Odoo Web Library) JavaScript framework, providing a dynamic, interactive, and real-time analytics experience.

## Features

### 1. Real-Time KPI Cards
- **Active Students**: Click to view all active students
- **Fees Collected**: Total fees collected with collection rate
- **Pending Fees**: Outstanding fees - click to view overdue
- **Attendance Rate**: Overall attendance percentage

### 2. Interactive Charts
All charts are powered by Chart.js and update dynamically:

#### Student Growth Chart
- Line chart showing enrollment trend over 12 months
- Hover to see exact numbers

#### Gender Distribution
- Doughnut chart showing male/female ratio
- Interactive legend

#### Grade Distribution
- Bar chart showing students per grade
- Color-coded for easy reading

#### Fee Collection by Grade
- Stacked bar chart
- Shows collected vs pending fees
- Compare across grades

#### Payment Status
- Pie chart showing paid/partial/unpaid
- Click legend to toggle sections

#### Attendance Trend
- Line chart for last 30 days
- Track daily attendance rates

#### Academic Grade Distribution
- Bar chart showing A, B, C, D, F counts
- Color-coded by performance

### 3. Upcoming Exams
- List of next 5 exams
- Shows date, name, and subject
- Automatically updates

### 4. Statistics Cards
Three detailed stat cards:
- Student Statistics
- Fee Statistics  
- Academic Statistics

## How to Use

### Accessing the Dashboard

Navigate to: **School → Dashboard → Main Dashboard**

### Refreshing Data

Click the **Refresh** button in the top-right corner to reload all data.

### Interacting with Charts

- **Hover**: See exact values
- **Click Legend**: Toggle data series
- **Responsive**: Works on all screen sizes

### Quick Actions

Click on KPI cards to:
- View students list
- Open fees management
- See overdue fees
- Access other modules

## Technical Details

### Architecture

```
┌─────────────────────────────────────┐
│         OWL Component               │
│  (school_dashboard.Dashboard)       │
└──────────────┬──────────────────────┘
               │
               ├─> RPC Controller
               │   (/school/dashboard/data)
               │
               ├─> Chart.js Rendering
               │   (8 different charts)
               │
               └─> State Management
                   (useState hook)
```

### Data Flow

1. Component loads → `onWillStart` hook
2. RPC call to `/school/dashboard/data`
3. Controller fetches data from models
4. Data returned as JSON
5. State updated
6. Charts rendered with Chart.js

### Files Structure

```
school_dashboard/
├── controllers/
│   └── main.py          # RPC endpoints
├── static/src/
│   ├── js/
│   │   └── dashboard.js # OWL component
│   ├── xml/
│   │   └── dashboard.xml # OWL template
│   └── css/
│       └── dashboard.css # Styles
└── views/
    └── dashboard_views.xml # Actions & menus
```

## Customization

### Adding New KPIs

1. Update controller in `controllers/main.py`:
```python
def _get_kpis(self):
    return {
        'my_kpi': calculate_my_kpi(),
        # ... existing KPIs
    }
```

2. Update template in `static/src/xml/dashboard.xml`:
```xml
<div class="kpi_card">
    <div class="kpi_value">
        <t t-esc="state.kpis.my_kpi"/>
    </div>
    <div class="kpi_label">My KPI</div>
</div>
```

### Adding New Charts

1. Add data method in controller:
```python
def _get_my_chart_data(self):
    return [{'label': 'A', 'value': 10}]
```

2. Add to `_get_chart_data()`:
```python
return {
    'my_chart': self._get_my_chart_data(),
    # ... existing charts
}
```

3. Add canvas in template:
```xml
<div class="chart_card">
    <canvas id="myChart"/>
</div>
```

4. Add render method in JS:
```javascript
renderMyChart() {
    const canvas = document.getElementById('myChart');
    const ctx = canvas.getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {...},
        options: {...}
    });
}
```

5. Call in `renderCharts()`:
```javascript
renderCharts() {
    this.renderMyChart();
    // ... existing renders
}
```

### Styling

Edit `static/src/css/dashboard.css`:

```css
/* Custom KPI card color */
.kpi_card.kpi_custom {
    color: #your-color;
}

/* Custom chart size */
.chart_card.chart_custom {
    grid-column: span 2;
    min-height: 400px;
}
```

## Performance

### Optimization Tips

1. **Lazy Loading**: Charts render only after data loads
2. **Single RPC Call**: All data fetched in one request
3. **Caching**: Browser caches static assets
4. **Responsive**: Adapts to screen size

### Load Times

- Initial load: ~1-2 seconds
- Refresh: ~500ms
- Chart render: ~200ms per chart

## Troubleshooting

### Dashboard Not Loading

**Check:**
1. Module installed correctly
2. JavaScript console for errors
3. Chart.js library loaded
4. User has access rights

**Fix:**
```bash
# Restart Odoo
# Clear browser cache
# Check Odoo logs
```

### Charts Not Rendering

**Check:**
1. Canvas elements exist in DOM
2. Chart.js loaded
3. Data format is correct
4. No JavaScript errors

**Fix:**
```javascript
// Add console.log in renderCharts()
console.log('Rendering charts with data:', this.state.charts);
```

### Data Not Updating

**Check:**
1. RPC endpoint responding
2. Controller returning data
3. State updating correctly

**Fix:**
```javascript
// Check network tab in browser
// Verify RPC response
```

### Slow Performance

**Optimize:**
1. Reduce data points in charts
2. Add pagination to lists
3. Cache computed values
4. Use database indexes

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Mobile Support

Dashboard is fully responsive:
- Tablets: 2-column layout
- Phones: Single column
- Touch-friendly interactions

## Keyboard Shortcuts

- `Ctrl+R` / `Cmd+R`: Refresh dashboard
- `Tab`: Navigate between cards
- `Enter`: Activate focused card

## Accessibility

- ARIA labels on all interactive elements
- Keyboard navigation support
- Screen reader compatible
- High contrast mode support

## API Endpoints

### Get Dashboard Data
```
POST /school/dashboard/data
Auth: user
Returns: {kpis, student_stats, fee_stats, academic_stats, charts}
```

### Refresh Dashboard
```
POST /school/dashboard/refresh
Auth: user
Returns: Same as /data
```

### Get Student Details
```
POST /school/dashboard/student/<id>
Auth: user
Returns: {id, name, code, grade, section, ...}
```

## Best Practices

1. **Regular Refresh**: Click refresh for latest data
2. **Use Filters**: Apply date/grade filters in analytics
3. **Export Data**: Use print/export for reports
4. **Monitor KPIs**: Check daily for trends
5. **Act on Alerts**: Address overdue fees promptly

## Future Enhancements

Planned features:
- Real-time updates via websockets
- Customizable dashboard layouts
- Drag-and-drop widgets
- Export to PDF/Excel
- Email scheduled reports
- Comparison with previous periods
- Predictive analytics
- Mobile app

## Support

For issues or questions:
1. Check browser console
2. Review Odoo logs
3. Verify data in database
4. Contact system administrator

## Version History

### 1.0.0 (2026-02-11)
- Initial OWL dashboard release
- 8 interactive charts
- 4 KPI cards
- Real-time data loading
- Responsive design
- Chart.js integration

---

**Enjoy your new dynamic dashboard!** 📊✨
