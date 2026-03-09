# School API v2 - HTTP REST Guide

Complete guide for the HTTP REST API with proper status codes.

## Base URL
```
http://localhost:8069/api/v2
```

## Authentication Flow

### 1. Login
**Endpoint:** `POST /api/v2/auth/login`  
**Auth:** None  
**Status Codes:** 200, 400, 401, 500

**Request:**
```json
{
  "db": "odoo18",
  "login": "admin",
  "password": "admin"
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "session_id": "akdqC7YDuBHfXs0IkH...",
  "uid": 2,
  "name": "Mitchell Admin",
  "is_student": false,
  "student_id": false,
  "company_name": "My Company"
}
```

**Error Response (401):**
```json
{
  "error": "Authentication Failed",
  "message": "Invalid username or password"
}
```

**Error Response (400):**
```json
{
  "error": "Missing Credentials",
  "message": "login and password are required"
}
```

### 2. Check Session
**Endpoint:** `GET/POST /api/v2/auth/check`  
**Auth:** User (requires session)  
**Status Codes:** 200, 401, 500

**Success Response (200):**
```json
{
  "status": "authenticated",
  "uid": 2,
  "name": "Admin User",
  "login": "admin",
  "company_name": "My Company"
}
```

**Error Response (401):**
```json
{
  "error": "Not Authenticated",
  "message": "No valid session found"
}
```

### 3. Logout
**Endpoint:** `POST /api/v2/auth/logout`  
**Auth:** User (requires session)  
**Status Codes:** 200, 500

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

## Student APIs

### Get Student Profile
**Endpoint:** `POST /api/v2/student/profile`  
**Auth:** User  
**Status Codes:** 200, 400, 403, 404, 500

**Request:**
```json
{
  "student_code": "STU001"
}
```

**Success Response (200):**
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

**Error Responses:**
- **400:** Missing student_code parameter
- **403:** Insufficient permissions
- **404:** Student not found
- **500:** Server error

### List Students
**Endpoint:** `POST /api/v2/student/list`  
**Auth:** User  
**Status Codes:** 200, 403, 500

**Request:**
```json
{
  "grade_id": 1,
  "section_id": 1,
  "limit": 50,
  "offset": 0
}
```

**Success Response (200):**
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

---

## Fee APIs

### Get Student Fees
**Endpoint:** `POST /api/v2/fees/student`  
**Auth:** User  
**Status Codes:** 200, 400, 403, 404, 500

**Request:**
```json
{
  "student_code": "STU001"
}
```

**Success Response (200):**
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

### Record Payment
**Endpoint:** `POST /api/v2/fees/payment/record`  
**Auth:** User  
**Status Codes:** 200, 400, 403, 404, 500

**Request:**
```json
{
  "fee_id": 123,
  "amount": 5000.00,
  "payment_reference": "PAY123456",
  "payment_date": "2026-02-14",
  "journal_id": 5
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "message": "Payment recorded and reconciled successfully",
  "data": {
    "fee_id": 123,
    "fee_display_name": "John Doe - 2025/2026 - Term 1",
    "invoice_id": 456,
    "invoice_number": "INV/2026/0001",
    "invoice_state": "posted",
    "payment_id": 789,
    "payment_name": "PBNK1/2026/0001",
    "payment_state": "paid",
    "amount_paid": 5000.0,
    "invoice_payment_state": "partial",
    "invoice_amount_total": 25000.0,
    "invoice_amount_residual": 20000.0,
    "payment_reference": "PAY123456",
    "payment_date": "2026-02-14",
    "journal_name": "Bank"
  }
}
```

**Error Responses:**
- **400:** Missing parameters, already paid, invalid journal
- **403:** Insufficient permissions
- **404:** Fee not found
- **500:** Invoice generation failed, payment creation failed

---

## Attendance APIs

### Get Student Attendance
**Endpoint:** `POST /api/v2/attendance/student`  
**Auth:** User  
**Status Codes:** 200, 400, 403, 404, 500

**Request:**
```json
{
  "student_code": "STU001",
  "date_from": "2026-01-01",
  "date_to": "2026-02-14"
}
```

**Success Response (200):**
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

## Complete Example with cURL

```bash
# 1. Login
curl -v -X POST http://localhost:8069/api/v2/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{
    "db": "odoo18",
    "login": "admin",
    "password": "admin"
  }'

# 2. Check session (optional)
curl -v -X GET http://localhost:8069/api/v2/auth/check \
  -b cookies.txt

# 3. Get student profile
curl -v -X POST http://localhost:8069/api/v2/student/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_code": "STU001"}'

# 4. Get student fees
curl -v -X POST http://localhost:8069/api/v2/fees/student \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_code": "STU001"}'

# 5. Record payment
curl -v -X POST http://localhost:8069/api/v2/fees/payment/record \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "fee_id": 19,
    "amount": 1800.00,
    "payment_reference": "PAY123456",
    "payment_date": "2026-02-14"
  }'

# 6. Get attendance
curl -v -X POST http://localhost:8069/api/v2/attendance/student \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "student_code": "STU001",
    "date_from": "2026-01-01",
    "date_to": "2026-02-14"
  }'

# 7. Logout
curl -v -X POST http://localhost:8069/api/v2/auth/logout \
  -b cookies.txt
```

---

## JavaScript/Fetch Example

```javascript
// 1. Login
const loginResponse = await fetch('http://localhost:8069/api/v2/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    db: 'odoo18',
    login: 'admin',
    password: 'admin'
  })
});

if (loginResponse.status === 200) {
  const loginData = await loginResponse.json();
  console.log('Logged in:', loginData);
  
  // 2. Get student profile
  const profileResponse = await fetch('http://localhost:8069/api/v2/student/profile', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ student_code: 'STU001' })
  });
  
  if (profileResponse.status === 200) {
    const profileData = await profileResponse.json();
    console.log('Student:', profileData.data);
  } else if (profileResponse.status === 404) {
    console.error('Student not found');
  } else {
    const error = await profileResponse.json();
    console.error('Error:', error.message);
  }
  
  // 3. Record payment
  const paymentResponse = await fetch('http://localhost:8069/api/v2/fees/payment/record', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({
      fee_id: 19,
      amount: 1800.00,
      payment_reference: 'PAY123456',
      payment_date: '2026-02-14'
    })
  });
  
  if (paymentResponse.status === 200) {
    const paymentData = await paymentResponse.json();
    console.log('Payment recorded:', paymentData.data);
  } else if (paymentResponse.status === 400) {
    const error = await paymentResponse.json();
    console.error('Payment error:', error.message);
  }
  
} else if (loginResponse.status === 401) {
  console.error('Invalid credentials');
} else {
  const error = await loginResponse.json();
  console.error('Login error:', error.message);
}
```

---

## HTTP Status Code Reference

| Code | Meaning | Common Causes |
|------|---------|---------------|
| **200** | OK | Request successful |
| **400** | Bad Request | Missing parameters, invalid data, business logic error (e.g., already paid) |
| **401** | Unauthorized | Invalid credentials, session expired |
| **403** | Forbidden | User doesn't have required permissions |
| **404** | Not Found | Student/fee/resource doesn't exist |
| **500** | Server Error | Internal error, database issue, unexpected exception |

---

## Error Handling Best Practices

```javascript
async function apiCall(url, data) {
  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data)
    });
    
    const result = await response.json();
    
    // Check HTTP status
    if (response.status === 200) {
      return { success: true, data: result };
    } else if (response.status === 401) {
      // Session expired - redirect to login
      window.location.href = '/login';
      return { success: false, error: 'Session expired' };
    } else if (response.status === 404) {
      return { success: false, error: 'Resource not found' };
    } else {
      return { success: false, error: result.message || 'Unknown error' };
    }
  } catch (error) {
    console.error('Network error:', error);
    return { success: false, error: 'Network error' };
  }
}

// Usage
const result = await apiCall('http://localhost:8069/api/v2/student/profile', {
  student_code: 'STU001'
});

if (result.success) {
  console.log('Student data:', result.data);
} else {
  console.error('Error:', result.error);
}
```

---

## Advantages of v2 HTTP API

✅ **Proper HTTP Status Codes** - Easy error handling in clients  
✅ **RESTful Design** - Standard HTTP semantics  
✅ **Clean JSON** - No JSON-RPC wrapper  
✅ **Session Security** - Secure cookie-based authentication  
✅ **Mobile-Friendly** - Works great with mobile HTTP clients  
✅ **Standard Tools** - Works with any HTTP client (curl, Postman, etc.)  

---

## Migration from JSON-RPC to HTTP

**Before (JSON-RPC):**
```javascript
fetch('/api/student/profile', {
  body: JSON.stringify({
    jsonrpc: "2.0",
    params: { student_code: "STU001" }
  })
})
```

**After (HTTP):**
```javascript
const response = await fetch('/api/v2/student/profile', {
  body: JSON.stringify({ student_code: "STU001" })
});

// Now you can check response.status!
if (response.status === 404) {
  console.error('Student not found');
}
```

The HTTP version is cleaner and provides proper status codes for better error handling!
