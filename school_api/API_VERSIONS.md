# School API - Version Comparison

This document compares the three versions of the School API available in the system.

## API Versions Overview

| Version | Auth Method | Response Format | HTTP Status Codes | Use Case |
|---------|-------------|-----------------|-------------------|----------|
| **v1** (Legacy) | API Key Header | HTTP JSON | Always 200 | External integrations, backward compatibility |
| **v2 JSON-RPC** | Session Cookie | JSON-RPC | Always 200 | Web applications, standard Odoo clients |
| **v2 HTTP** | Session Cookie | REST JSON | Proper codes | Modern REST clients, mobile apps |

---

## Version 1: API Key Authentication (Legacy)

**Authentication:** API Key via `X-Api-Key` header  
**Base Path:** `/api/v1/`  
**Type:** HTTP with JSON body  
**Status Codes:** Always returns 200 OK

### Endpoints:
- `POST /api/v1/student/profile` - Get student profile
- `POST /api/v1/student/list` - List students
- `POST /api/v1/fees/student` - Get student fees
- `POST /api/v1/fees/payment/record` - Record payment
- `POST /api/v1/attendance/student` - Get attendance

### Example Request:
```bash
curl -X POST http://localhost:8069/api/v1/student/profile \
  -H "X-Api-Key: sk_your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{"student_code": "STU001"}'
```

### Response Format:
```json
{
  "status": "success",
  "data": { ... }
}
```

**Pros:**
- No session management needed
- Simple authentication
- Good for server-to-server communication

**Cons:**
- Always returns HTTP 200 (even for errors)
- Requires API key management
- Less secure than session-based auth

---

## Version 2: JSON-RPC Session Authentication

**Authentication:** Session cookie (login required)  
**Base Path:** `/api/`  
**Type:** JSON-RPC  
**Status Codes:** Always returns 200 OK

### Endpoints:
- `POST /api/auth/login` - Login and get session
- `POST /api/auth/logout` - Logout
- `POST /api/student/profile` - Get student profile
- `POST /api/student/list` - List students
- `POST /api/fees/student` - Get student fees
- `POST /api/fees/payment/record` - Record payment
- `POST /api/attendance/student` - Get attendance

### Example Request:
```bash
# 1. Login first
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

# 2. Use session for API calls
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

### Response Format:
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "result": {
    "status": "success",
    "data": { ... }
  }
}
```

**Pros:**
- Standard Odoo JSON-RPC format
- Session-based security
- Compatible with Odoo web client patterns

**Cons:**
- Always returns HTTP 200 (even for errors)
- Requires session management
- More complex for simple integrations

---

## Version 2: HTTP REST Session Authentication (Recommended)

**Authentication:** Session cookie (login required)  
**Base Path:** `/api/v2/`  
**Type:** HTTP REST with JSON  
**Status Codes:** Proper HTTP codes (200, 400, 403, 404, 500)

### Endpoints:
- `POST /api/auth/login` - Login and get session (JSON-RPC)
- `POST /api/auth/logout` - Logout (JSON-RPC)
- `POST /api/v2/student/profile` - Get student profile
- `POST /api/v2/student/list` - List students
- `POST /api/v2/fees/student` - Get student fees
- `POST /api/v2/fees/payment/record` - Record payment
- `POST /api/v2/attendance/student` - Get attendance

### Example Request:
```bash
# 1. Login first (JSON-RPC)
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

# 2. Use session for API calls (HTTP REST)
curl -X POST http://localhost:8069/api/v2/student/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_code": "STU001"}'
```

### Success Response (HTTP 200):
```json
{
  "status": "success",
  "data": {
    "name": "John Doe",
    "code": "STU001",
    ...
  }
}
```

### Error Response (HTTP 400/403/404/500):
```json
{
  "error": "Not Found",
  "message": "No student found with this code"
}
```

**Pros:**
- ✅ Proper HTTP status codes
- ✅ RESTful design
- ✅ Session-based security
- ✅ Easy error handling
- ✅ Standard HTTP semantics

**Cons:**
- Requires session management
- Login uses JSON-RPC (for compatibility)

---

## HTTP Status Codes (v2 HTTP Only)

| Code | Meaning | When Used |
|------|---------|-----------|
| 200 | OK | Successful request |
| 400 | Bad Request | Missing parameters, invalid data, business logic errors |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal server error, unexpected exceptions |

---

## API Comparison Table

### Student Profile Endpoint

| Feature | v1 API Key | v2 JSON-RPC | v2 HTTP |
|---------|------------|-------------|---------|
| **Endpoint** | `/api/v1/student/profile` | `/api/student/profile` | `/api/v2/student/profile` |
| **Auth** | API Key | Session | Session |
| **Request Type** | HTTP | JSON-RPC | HTTP |
| **Success Status** | 200 | 200 | 200 |
| **Error Status** | 200 | 200 | 400/403/404/500 |
| **Error in Body** | ✅ | ✅ | ✅ |
| **Error in Header** | ❌ | ❌ | ✅ |

### Payment Record Endpoint

| Feature | v1 API Key | v2 JSON-RPC | v2 HTTP |
|---------|------------|-------------|---------|
| **Endpoint** | `/api/v1/fees/payment/record` | `/api/fees/payment/record` | `/api/v2/fees/payment/record` |
| **Auth** | API Key | Session | Session |
| **Invoice Generation** | ✅ | ✅ | ✅ |
| **Partial Payments** | ✅ | ✅ | ✅ |
| **Auto Reconciliation** | ✅ | ✅ | ✅ |
| **Proper Status Codes** | ❌ | ❌ | ✅ |

---

## Migration Guide

### From v1 (API Key) to v2 HTTP

**Before (v1):**
```javascript
fetch('http://localhost:8069/api/v1/student/profile', {
  method: 'POST',
  headers: {
    'X-Api-Key': 'sk_your_key',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ student_code: 'STU001' })
})
```

**After (v2 HTTP):**
```javascript
// 1. Login once
const loginRes = await fetch('http://localhost:8069/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({
    jsonrpc: "2.0",
    params: { db: "odoo18", login: "admin", password: "admin" }
  })
});

// 2. Use session for all requests
const profileRes = await fetch('http://localhost:8069/api/v2/student/profile', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  credentials: 'include',
  body: JSON.stringify({ student_code: 'STU001' })
});

// 3. Check HTTP status
if (profileRes.status === 404) {
  console.error('Student not found');
} else if (profileRes.status === 200) {
  const data = await profileRes.json();
  console.log(data);
}
```

---

## Recommendations

### Use v1 (API Key) when:
- Building server-to-server integrations
- Need simple authentication without sessions
- Backward compatibility required
- Don't need proper HTTP status codes

### Use v2 JSON-RPC when:
- Building Odoo web modules
- Need standard Odoo patterns
- Working with Odoo's JavaScript framework

### Use v2 HTTP when: ⭐ **Recommended**
- Building modern REST APIs
- Need proper HTTP status codes
- Building mobile applications
- Want standard REST semantics
- Need easy error handling in clients

---

## Security Notes

1. **Always use HTTPS in production** - All authentication methods transmit credentials
2. **API Keys** - Store securely, rotate regularly, use different keys per client
3. **Sessions** - Set proper session timeout, use secure cookies
4. **CORS** - Configure properly if calling from web applications
5. **Rate Limiting** - Implement for production environments

---

## Testing Examples

### Test v2 HTTP API with curl:

```bash
# Login
curl -v -X POST http://localhost:8069/api/auth/login \
  -H "Content-Type: application/json" \
  -c cookies.txt \
  -d '{"jsonrpc":"2.0","params":{"db":"odoo18","login":"admin","password":"admin"}}'

# Test success (HTTP 200)
curl -v -X POST http://localhost:8069/api/v2/student/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_code":"STU001"}'

# Test not found (HTTP 404)
curl -v -X POST http://localhost:8069/api/v2/student/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"student_code":"INVALID"}'

# Test missing parameter (HTTP 400)
curl -v -X POST http://localhost:8069/api/v2/student/profile \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{}'
```

The `-v` flag shows HTTP status codes in the response headers.
