# Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- Odoo 18 running on `http://localhost:8069`
- School API module installed and configured in Odoo

## Installation & Run

```bash
# Navigate to the portal directory
cd external_apps/school_portal_ui

# Install dependencies
npm install

# Start development server
npm run dev
```

The portal will open at `http://localhost:3000`

## First Login

1. Open `http://localhost:3000` in your browser
2. Enter your credentials:
   - **Database**: `odoo18` (or your database name)
   - **Username**: Your Odoo username (e.g., `admin`)
   - **Password**: Your Odoo password
3. Click "Login"

## Features Overview

### Dashboard
- Quick overview of fees, attendance, and student info
- Summary cards with key metrics
- Recent fee records

### Fees
- View all fee records
- See payment status (Paid, Partially Paid, Unpaid)
- Make payments with payment modal
- Filter and search fees

### Attendance
- View attendance records in table format
- Filter by date range
- Visual charts (pie chart and bar chart)
- Attendance statistics and percentage

### Profile
- Student personal information
- Academic information
- Parent/Guardian details

## Troubleshooting

### CORS Issues
If you see CORS errors, make sure:
1. Odoo is running on `http://localhost:8069`
2. The Vite proxy is configured correctly in `vite.config.js`
3. Restart the dev server after config changes

### Session Expired
If you get "Session Expired" errors:
1. Login again
2. Check that cookies are enabled in your browser
3. Verify Odoo session timeout settings

### API Errors
If API calls fail:
1. Check that the `school_api` module is installed in Odoo
2. Verify the HTTP API endpoints are accessible
3. Check Odoo logs for errors
