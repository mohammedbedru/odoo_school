# School API Documentation

## Authentication

### Login API
**Endpoint:** `/api/auth/login`  
**Method:** POST  
**Auth:** None  
**Type:** JSON-RPC

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "db": "odoo18",
    "login": "admin",
    "password": "admin"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": "success",
    "session_id": "akdqC7YDuBHfXs0IkH...",
    "uid": 2,
    "name": "Mitchell Admin",
    "is_student": false,
    "student_id": false,
    "company_name": "My Company"
  }
}
```

### Logout API
**Endpoint:** `/api/auth/logout`  
**Method:** POST  
**Auth:** User (requires session)  
**Type:** JSON-RPC

**Response:**
```json
{
  "status": "success",
  "message": "Logged out"
}
```

---

## Session-Based APIs

All session-based APIs require authentication via the login endpoint first. Include the `session_id` in cookies.

### Student APIs

#### Get Student Profile
**Endpoint:** `/api/student/profile`  
**Method:** POST  
**Auth:** User  
**Type:** JSON-RPC

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "student_code": "STU001"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "name": "John Doe",
    "code": "STU001",
    "grade": "Grade 10",
    "section": "A",
    "gender": "male",
    "age": 15,
    "date_of_birth": "2011-01-15",
    "email": "john@example.com",
    "phone": "1234567890",
    "parents": [
      {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "9876543210"
      }
    ],
    "fee_summary": {
      "total_fees": 50000.0,
      "paid_amount": 30000.0,
      "pending_amount": 20000.0,
      "overdue_count": 1
    }
  }
}
```

#### List Students
**Endpoint:** `/api/student/list`  
**Method:** POST  
**Auth:** User  
**Type:** JSON-RPC

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "grade_id": 1,
    "section_id": 1,
    "limit": 50,
    "offset": 0
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "students": [
      {
        "id": 1,
        "name": "John Doe",
        "code": "STU001",
        "grade": "Grade 10",
        "section": "A",
        "email": "john@example.com"
      }
    ],
    "total_count": 100,
    "limit": 50,
    "offset": 0
  }
}
```

### Fee APIs

#### Get Student Fees
**Endpoint:** `/api/fees/student`  
**Method:** POST  
**Auth:** User  
**Type:** JSON-RPC

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "student_code": "STU001"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "student": {
      "name": "John Doe",
      "code": "STU001"
    },
    "fees": [
      {
        "id": 1,
        "display_name": "Tuition Fee - Term 1",
        "academic_year": "2025-2026",
        "term": "Term 1",
        "amount_total": 25000.0,
        "amount_paid": 15000.0,
        "amount_due": 10000.0,
        "state": "confirmed",
        "payment_state": "partial",
        "due_date": "2026-03-31"
      }
    ],
    "summary": {
      "total": 50000.0,
      "paid": 30000.0,
      "due": 20000.0
    }
  }
}
```

#### Record Payment
**Endpoint:** `/api/fees/payment/record`  
**Method:** POST  
**Auth:** User  
**Type:** JSON-RPC

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "fee_id": 123,
    "amount": 5000.00,
    "payment_reference": "PAY123456",
    "payment_date": "2026-02-14"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Payment recorded and reconciled successfully",
  "data": {
    "fee_id": 123,
    "invoice_id": 456,
    "invoice_number": "INV/2026/0001",
    "payment_id": 789,
    "payment_name": "BNK1/2026/0001",
    "amount_paid": 5000.0,
    "invoice_payment_state": "paid",
    "invoice_amount_residual": 0.0,
    "payment_reference": "PAY123456"
  }
}
```

### Attendance APIs

#### Get Student Attendance
**Endpoint:** `/api/attendance/student`  
**Method:** POST  
**Auth:** User  
**Type:** JSON-RPC

**Request:**
```json
{
  "jsonrpc": "2.0",
  "params": {
    "student_code": "STU001",
    "date_from": "2026-01-01",
    "date_to": "2026-02-14"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "student": {
      "name": "John Doe",
      "code": "STU001"
    },
    "attendance": [
      {
        "date": "2026-01-15",
        "status": "present",
        "remarks": ""
      },
      {
        "date": "2026-01-16",
        "status": "absent",
        "remarks": "Sick leave"
      }
    ],
    "summary": {
      "total_days": 30,
      "present": 28,
      "absent": 2,
      "attendance_percentage": 93.33
    }
  }
}
```

---

## API Key-Based APIs (Legacy)

These APIs use API Key authentication via the `X-Api-Key` header. They remain available for backward compatibility.

### Endpoints:
- `/api/v1/student/profile` - Get student profile
- `/api/v1/student/list` - List students
- `/api/v1/fees/student` - Get student fees
- `/api/v1/fees/payment/record` - Record payment
- `/api/v1/attendance/student` - Get student attendance

**Authentication Header:**
```
X-Api-Key: sk_your_api_key_here
Content-Type: application/json
```

---

## Error Responses

All APIs return errors in this format:

```json
{
  "status": "error",
  "error": "Error Type",
  "message": "Detailed error message"
}
```

**Common Error Codes:**
- `400` - Bad Request (missing parameters, invalid JSON)
- `401` - Unauthorized (invalid credentials or session)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `500` - Server Error (internal error)

---

## Usage Examples

### Using cURL with Session Authentication

1. **Login:**
```bash
curl -X POST http://localhost:8069/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "params": {
      "db": "odoo18",
      "login": "admin",
      "password": "admin"
    }
  }'
```

2. **Get Student Profile:**
```bash
curl -X POST http://localhost:8069/api/student/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "jsonrpc": "2.0",
    "params": {
      "student_code": "STU001"
    }
  }'
```

### Using JavaScript/Fetch

```javascript
// Login
const loginResponse = await fetch('http://localhost:8069/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    jsonrpc: "2.0",
    params: {
      db: "odoo18",
      login: "admin",
      password: "admin"
    }
  })
});

const loginData = await loginResponse.json();
console.log('Session ID:', loginData.result.session_id);

// Get Student Profile
const profileResponse = await fetch('http://localhost:8069/api/student/profile', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    jsonrpc: "2.0",
    params: {
      student_code: "STU001"
    }
  })
});

const profileData = await profileResponse.json();
console.log('Student:', profileData.result.data);
```

---

## Notes

1. **Session Management:** Sessions expire after inactivity. Re-login if you receive 401 errors.
2. **Database Parameter:** The `db` parameter in login is required for multi-database setups.
3. **CORS:** Configure CORS headers in Odoo if calling from a web application.
4. **HTTPS:** Always use HTTPS in production to protect credentials.
5. **Rate Limiting:** Consider implementing rate limiting for production use.
