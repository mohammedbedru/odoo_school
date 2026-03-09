# School Portal Installation & Testing Guide

## Installation Steps

1. **Install the module**
   - Go to Apps menu
   - Search for "School Portal"
   - Click Install

2. **Verify Installation**
   - Check that no errors occurred during installation
   - The portal menu should be added to the Odoo portal homepage

## Granting Portal Access

### For Students

1. Go to **School → Students**
2. Open a student record (must have an email address)
3. Click the **"Grant Portal Access"** button in the header
4. A portal user will be created and:
   - **Option A**: A password reset email is sent to the student's email
   - **Option B**: If email fails, a temporary password is shown in the notification
5. The student can login at `/web/login` using their email as login

### For Parents

1. Go to **School → Parents/Guardians**
2. Open a parent record (must have an email address)
3. Click the **"Grant Portal Access"** button in the header
4. A portal user will be created and:
   - **Option A**: A password reset email is sent to the parent's email
   - **Option B**: If email fails, a temporary password is shown in the notification
5. The parent can login at `/web/login` using their email as login

### Password Management

- **Automatic**: Users receive a password reset link via email (recommended)
- **Manual**: If email is not configured, copy the temporary password from the notification
- **Reset**: Users can always reset their password using the "Reset Password" link on the login page
- **Change**: Users can change their password after logging in from their profile

## Portal Features

### Student Portal (`/my/student/dashboard`)
- View profile information
- Check timetable
- View attendance records
- Check exam marks
- Download report cards
- View fee status and payment history

### Parent Portal (`/my/parent/children`)
- View list of children
- Access each child's:
  - Profile
  - Attendance
  - Marks
  - Report cards
  - Fee status
- Download PDFs

## Security

- Students can only see their own records
- Parents can only see their children's records
- All data is protected by record rules
- Portal users cannot modify any data

## Testing Checklist

- [ ] Module installs without errors
- [ ] Student portal access can be granted
- [ ] Parent portal access can be granted
- [ ] Student can login and view dashboard
- [ ] Parent can login and view children
- [ ] Portal menu appears on homepage
- [ ] Record rules prevent unauthorized access
- [ ] PDFs can be downloaded
- [ ] Portal access can be revoked

## Troubleshooting

### Portal menu not showing
- Clear browser cache
- Restart Odoo server
- Update the module

### Cannot grant portal access
- Ensure student/parent has an email address
- Check that portal groups exist in Settings → Users & Companies → Groups

### Portal user cannot see data
- Verify record rules are active
- Check that user_id field is set correctly
- Ensure student/parent relationship is properly configured
