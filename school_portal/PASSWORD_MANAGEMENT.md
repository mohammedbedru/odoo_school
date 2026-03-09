# Portal Password Management

## How It Works

When you grant portal access to a student or parent, the system:

1. **Generates a secure random password** (12 characters with letters, numbers, and special characters)
2. **Creates the portal user account** with that password
3. **Attempts to send a password reset email** to the user's email address
4. **Shows a notification** with the result

## Two Scenarios

### Scenario A: Email Configured (Recommended)
If your Odoo instance has outgoing email configured:
- User receives an email with a "Reset Password" link
- They click the link and set their own password
- Notification shows: "Portal access granted. Password reset email sent to [email]"

### Scenario B: Email Not Configured
If email is not configured or fails:
- Notification shows the temporary password
- Example: "Portal access granted. Login: john@example.com | Temporary Password: aB3$xY9#mK2p"
- **Important**: Copy this password immediately and share it securely with the user

## User Login Process

1. Go to `/web/login`
2. Enter email as login
3. Enter password (from reset email or temporary password)
4. Click "Log in"

## Password Reset

Users can reset their password anytime:

1. On login page, click "Reset Password"
2. Enter their email address
3. Receive reset link via email
4. Set new password

## Security Best Practices

- Always use email-based password reset when possible
- If sharing temporary passwords, use secure channels (not SMS or public chat)
- Encourage users to change their password after first login
- Temporary passwords are only shown once - copy them immediately

## Configuring Outgoing Email

To enable automatic password reset emails:

1. Go to **Settings → Technical → Outgoing Mail Servers**
2. Configure your SMTP server
3. Test the connection
4. Set as default server

Common SMTP settings:
- **Gmail**: smtp.gmail.com:587 (TLS)
- **Outlook**: smtp.office365.com:587 (TLS)
- **SendGrid**: smtp.sendgrid.net:587 (TLS)

## Troubleshooting

### User didn't receive reset email
- Check spam/junk folder
- Verify email address is correct
- Check Odoo email logs: Settings → Technical → Email → Emails
- Manually send reset: Settings → Users & Companies → Users → [user] → Send Password Reset Instructions

### Forgot to copy temporary password
- Revoke portal access
- Grant portal access again (generates new password)

### User cannot login
- Verify email is correct
- Try password reset
- Check user is active: Settings → Users & Companies → Users
- Verify user has portal group assigned
