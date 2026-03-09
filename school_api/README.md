# School API Module

REST API for third-party integration with the school management system.

## Features

- Secure API key authentication
- Student profile and listing endpoints
- Fee management and payment recording
- Attendance tracking
- Usage monitoring and analytics

## Installation

1. Install the module from Apps menu
2. Go to School > API Management > API Keys
3. Create a new API key
4. Copy the generated key (it's shown only once!)

## API Endpoints

### Authentication

All API requests require an API key in the header:
```
X-Api-Key: sk_your_api_key_here
```

### Student Endpoints

#### Get Student Profile
```
POST /api/v1/student/profile
Content-Type: application/json

{
    "student_code": "STU001"
}
```

Response:
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
        "email": "john@example.com",
        "parent": {
            "name": "Jane Doe",
            "email": "jane@example.com"
        },
        "fee_summary": {
            "total_fees": 50000,
            "paid_amount": 30000,
            "pending_amount": 20000
        }
    }
}
```

#### List Students
```
POST /api/v1/student/list
Content-Type: application/json

{
    "grade_id": 1,
    "limit": 50,
    "offset": 0
}
```

### Fee Endpoints

#### Get Student Fees
```
POST /api/v1/fees/student
Content-Type: application/json

{
    "student_code": "STU001"
}
```

#### Record Payment (Webhook)
```
POST /api/v1/fees/payment/record
Content-Type: application/json

{
    "fee_id": 123,
    "amount": 5000.00,
    "payment_reference": "PAY123456",
    "payment_date": "2026-02-14"
}
```

### Attendance Endpoints

#### Get Student Attendance
```
POST /api/v1/attendance/student
Content-Type: application/json

{
    "student_code": "STU001",
    "date_from": "2026-01-01",
    "date_to": "2026-02-14"
}
```

## Testing with cURL

```bash
curl -X POST http://your-odoo-server/api/v1/student/profile \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: sk_your_api_key_here" \
  -d '{"student_code": "STU001"}'
```

## Testing with Python

```python
import requests

url = "http://your-odoo-server/api/v1/student/profile"
headers = {
    "Content-Type": "application/json",
    "X-Api-Key": "sk_your_api_key_here"
}
data = {"student_code": "STU001"}

response = requests.post(url, json=data, headers=headers)
print(response.json())
```

## Security Best Practices

1. Store API keys securely (use environment variables)
2. Rotate keys regularly
3. Deactivate unused keys
4. Monitor usage through the API Key management interface
5. Use HTTPS in production

## Error Responses

All errors follow this format:
```json
{
    "status": "error",
    "error": "Error Type",
    "message": "Detailed error message"
}
```

Common error codes:
- 401: Unauthorized (invalid API key)
- 404: Not Found (resource doesn't exist)
- 400: Bad Request (missing parameters)
- 500: Server Error (internal error)
