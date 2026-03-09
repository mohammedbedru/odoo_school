# Why We Use `auth='public'` for HTTP REST APIs

## The Problem

When building REST APIs in Odoo, we need to return JSON responses for all scenarios, including authentication failures. However, Odoo's default behavior with `auth='user'` causes issues for API endpoints.

## Odoo's Default Behavior with `auth='user'`

When you use `auth='user'` on an HTTP endpoint:

```python
@http.route('/api/v2/student/profile', type='http', auth='user', methods=['POST'])
def get_student_profile(self, **kwargs):
    # Your code here
```

**What happens when session expires:**
1. Odoo detects the session is invalid
2. Odoo automatically redirects to `/web/login`
3. Client receives an HTML login page instead of JSON
4. HTTP status code is 303 (redirect) or 200 (HTML page)

**Example response (BAD for APIs):**
```html
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
  <head><title>Odoo</title></head>
  <body>
    <form action="/web/login">
      <input name="login" />
      <input name="password" />
    </form>
  </body>
</html>
```

This breaks API clients that expect JSON responses!

## The Solution: `auth='public'` with Manual Session Check

By using `auth='public'`, we gain control over the authentication flow:

```python
@http.route('/api/v2/student/profile', type='http', auth='public', methods=['POST'])
def get_student_profile(self, **kwargs):
    # Manually check if user is authenticated
    if not request.session.uid or request.session.uid == request.env.ref('base.public_user').id:
        # Return JSON error with proper HTTP status code
        return request.make_json_response({
            'error': {
                'code': 100,
                'message': 'Odoo Session Expired',
                'data': {
                    'name': 'odoo.http.SessionExpiredException',
                    'message': 'Session expired',
                    'arguments': ['Session expired']
                }
            }
        }, status=401)
    
    # User is authenticated - proceed with request
    student = request.env['school.student'].search(...)
```

**What happens when session expires:**
1. Request proceeds normally (no automatic redirect)
2. We manually check `request.session.uid`
3. We return a JSON error response
4. HTTP status code is 401 (Unauthorized)

**Example response (GOOD for APIs):**
```json
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "error": {
    "code": 100,
    "message": "Odoo Session Expired",
    "data": {
      "name": "odoo.http.SessionExpiredException",
      "message": "Session expired",
      "arguments": ["Session expired"]
    }
  }
}
```

## Understanding Odoo's Auth Options

| Auth Type | Behavior | Use Case |
|-----------|----------|----------|
| `auth='none'` | No authentication, no session | Public endpoints (login page) |
| `auth='public'` | Session available, user may be public or authenticated | APIs that need to check auth manually |
| `auth='user'` | Requires authenticated user, redirects if not | Web pages, forms |

## Why `auth='public'` is Safe

Some developers worry that `auth='public'` means "no security". This is **not true**!

### Security is Maintained Because:

1. **Manual Session Check**: We explicitly verify the user is authenticated
   ```python
   if not request.session.uid or request.session.uid == public_user.id:
       return error_response(401)
   ```

2. **Permission Checks**: We verify user has required permissions
   ```python
   if not request.env.user.has_group('base.group_user'):
       return error_response(403)
   ```

3. **Record-Level Security**: Odoo's ORM still enforces record rules
   ```python
   # This respects user's access rights
   student = request.env['school.student'].search([...])
   ```

### It's Actually MORE Secure for APIs:

- ✅ Prevents information leakage (no HTML login page revealing system info)
- ✅ Proper error codes help clients handle auth failures correctly
- ✅ Consistent JSON responses make security testing easier
- ✅ No automatic redirects that could be exploited

## Comparison: JSON-RPC vs HTTP

### JSON-RPC (`type='json'`)
```python
@http.route('/api/student/profile', type='json', auth='user')
def get_student_profile(self, **kwargs):
    # Odoo handles session expiry automatically
    # Returns proper JSON-RPC error
```

**Session expired response:**
```json
{
  "jsonrpc": "2.0",
  "id": null,
  "error": {
    "code": 100,
    "message": "Odoo Session Expired",
    "data": {...}
  }
}
```
✅ Works correctly - Odoo's JSON-RPC dispatcher catches `SessionExpiredException`

### HTTP (`type='http'`) with `auth='user'`
```python
@http.route('/api/v2/student/profile', type='http', auth='user')
def get_student_profile(self, **kwargs):
    # Odoo redirects to login page
```

**Session expired response:**
```html
<!DOCTYPE html>
<html>...</html>
```
❌ Returns HTML - breaks API clients

### HTTP (`type='http'`) with `auth='public'`
```python
@http.route('/api/v2/student/profile', type='http', auth='public')
def get_student_profile(self, **kwargs):
    if not request.session.uid or request.session.uid == public_user.id:
        return json_error(401)
```

**Session expired response:**
```json
{
  "error": {
    "code": 100,
    "message": "Odoo Session Expired",
    "data": {...}
  }
}
```
✅ Returns JSON - works correctly for API clients

## Implementation Pattern

Here's the standard pattern we use in all v2 HTTP APIs:

```python
from odoo import http
from odoo.http import request

class MyHTTPAPI(http.Controller):
    
    def _check_session(self):
        """
        Check if user is authenticated.
        Returns JSON error response if not, None if authenticated.
        
        This method is called at the start of every endpoint to ensure
        we return JSON errors instead of HTML redirects when session expires.
        """
        if not request.session.uid or request.session.uid == request.env.ref('base.public_user').id:
            return request.make_json_response({
                'error': {
                    'code': 100,
                    'message': 'Odoo Session Expired',
                    'data': {
                        'name': 'odoo.http.SessionExpiredException',
                        'message': 'Session expired',
                        'arguments': ['Session expired']
                    }
                }
            }, status=401)
        return None
    
    @http.route('/api/v2/my/endpoint', type='http', auth='public', methods=['POST'], csrf=False)
    def my_endpoint(self, **kwargs):
        """
        My API endpoint.
        
        Note: We use auth='public' instead of auth='user' to prevent automatic
        redirects to the login page when session expires. This ensures API clients
        always receive JSON responses, not HTML pages.
        """
        # ALWAYS check session first
        session_error = self._check_session()
        if session_error:
            return session_error
        
        # Now we know user is authenticated
        # Proceed with business logic...
        data = request.env['my.model'].search([...])
        
        return request.make_json_response({
            'status': 'success',
            'data': data
        }, status=200)
```

## Benefits Summary

### For API Clients:
- ✅ Always receive JSON responses
- ✅ Proper HTTP status codes (401 for auth failures)
- ✅ Consistent error format
- ✅ Easy to detect and handle session expiry

### For Developers:
- ✅ Full control over authentication flow
- ✅ Consistent error handling across all endpoints
- ✅ Easy to customize error messages
- ✅ Better debugging (clear JSON errors vs HTML pages)

### For Security:
- ✅ No information leakage through HTML pages
- ✅ Explicit authentication checks
- ✅ Proper permission verification
- ✅ Odoo's record-level security still enforced

## Common Questions

### Q: Doesn't `auth='public'` mean anyone can access?
**A:** No! We manually check authentication. If the user isn't logged in, we return a 401 error. The endpoint is still protected.

### Q: Why not just use `auth='user'`?
**A:** Because `auth='user'` redirects to HTML login page when session expires. API clients expect JSON, not HTML.

### Q: Is this approach secure?
**A:** Yes! We explicitly check authentication and permissions. It's actually more secure because we control the entire flow.

### Q: Why does JSON-RPC work with `auth='user'`?
**A:** Odoo's JSON-RPC dispatcher has special handling for `SessionExpiredException` and returns proper JSON errors. HTTP endpoints don't have this.

### Q: Can I use `auth='none'` instead?
**A:** No! `auth='none'` means no session at all. We need the session to check if user is authenticated. `auth='public'` gives us a session.

## Conclusion

Using `auth='public'` with manual session checking is the **correct and recommended approach** for building REST APIs in Odoo when using `type='http'`. It ensures:

1. API clients always receive JSON responses
2. Proper HTTP status codes are returned
3. Security is maintained through explicit checks
4. Error handling is consistent and predictable

This pattern is used throughout our v2 HTTP API implementation to provide a professional, standards-compliant REST API experience.
