# School Portal UI

A beautiful React-based student/parent portal for the Odoo School Management System.

## Features

- **Dashboard**: Overview of student information, fees, and attendance
- **Fees Management**: View fee records, payment history, and make payments
- **Attendance Tracking**: View attendance records with charts and statistics
- **Profile**: Student and parent information

## Tech Stack

- React 19
- Vite
- Tailwind CSS
- React Router
- Axios
- Recharts (for charts)
- Lucide React (for icons)
- date-fns (for date formatting)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

The app will run on `http://localhost:3000` with proxy configured to connect to Odoo at `http://localhost:8069`.

## Build for Production

```bash
npm run build
```

The production build will be in the `dist` folder.

## Configuration

The Vite proxy is configured in `vite.config.js` to forward API requests to Odoo:
- `/api/*` → `http://localhost:8069/api/*`
- `/web/*` → `http://localhost:8069/web/*`

## API Endpoints Used

- `POST /api/v2/auth/login` - Login
- `POST /api/v2/auth/logout` - Logout
- `GET /api/v2/auth/check` - Check session
- `POST /api/v2/student/profile` - Get student profile
- `POST /api/v2/fees/student` - Get student fees
- `POST /api/v2/fees/payment/record` - Record payment
- `POST /api/v2/attendance/student` - Get attendance records

## Default Login

Use your Odoo credentials:
- Database: `odoo18` (or your database name)
- Username: Your Odoo username
- Password: Your Odoo password
