# School Portal UI - Setup Instructions

## Prerequisites
- Node.js 18+ installed
- Odoo server running on http://localhost:8069
- school_api module installed and activated in Odoo

## Installation

1. Install dependencies:
```bash
cd external_apps/school_portal_ui
npm install
```

2. Configure API endpoint (if different from localhost:8069):
Edit `src/services/api.js` and update the `BASE_URL` constant.

3. Start development server:
```bash
npm run dev
```

The app will be available at http://localhost:5173

## Building for Production

```bash
npm run build
```

The built files will be in the `dist` folder.

## Features

### Student Portal
- Dashboard with overview
- View grades and academic performance
- Check attendance records
- View and pay fees
- Download fee statements
- View announcements

### Parent Portal
- View all children's information
- Monitor academic performance
- Track attendance
- Manage fee payments
- Receive notifications

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── common/         # Common components (Button, Card, etc.)
│   ├── layout/         # Layout components (Header, Sidebar, etc.)
│   └── dashboard/      # Dashboard-specific components
├── pages/              # Page components
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── Fees.jsx
│   ├── Attendance.jsx
│   └── Profile.jsx
├── services/           # API services
│   └── api.js         # API client
├── context/            # React context providers
│   └── AuthContext.jsx
├── utils/              # Utility functions
│   └── helpers.js
├── App.jsx             # Main app component
└── main.jsx            # Entry point
```

## API Endpoints Used

- `POST /api/v2/auth/login` - Login
- `POST /api/v2/auth/logout` - Logout
- `GET /api/v2/auth/check` - Check session
- `POST /api/v2/student/profile` - Get student profile
- `POST /api/v2/fees/student` - Get student fees
- `POST /api/v2/fees/payment/record` - Record payment
- `POST /api/v2/attendance/student` - Get attendance

## Default Credentials

Use your Odoo credentials to login.

## Troubleshooting

### CORS Issues
If you encounter CORS errors, you need to configure Odoo to allow requests from your React app.

Add to your Odoo configuration file (odoo.conf):
```
[options]
proxy_mode = True
```

Or use a proxy in vite.config.js (already configured).

### Session Expired
If you get "Session Expired" errors, login again. Sessions expire after inactivity.

### API Connection Failed
Make sure:
1. Odoo server is running
2. school_api module is installed
3. API endpoint URL is correct in src/services/api.js
