# Clear Cache and Reload Assets

## The Problem
The JavaScript file isn't being loaded because Odoo has cached the old assets.

## Solution - Follow These Steps:

### Method 1: Clear Assets via URL (Easiest)
1. Open your browser
2. Go to: `http://localhost:8080/web/webclient/bundle?debug=assets`
3. This will force Odoo to rebuild all assets
4. Then go back to: `http://localhost:8080`
5. Navigate to **School → Dashboard → Main Dashboard**

### Method 2: Clear Browser Cache
1. Open browser DevTools (F12)
2. Right-click on the refresh button
3. Select "Empty Cache and Hard Reload"
4. Navigate to the dashboard

### Method 3: Restart Odoo with Assets Rebuild
1. Stop Odoo server
2. Start with: `./odoo-bin --dev=all`
3. Or add `?debug=assets` to your URL

### Method 4: Delete Assets from Database (Most Thorough)
Run this in Odoo shell or database:

```python
# In Odoo shell
env['ir.attachment'].search([('name', 'ilike', 'web.assets_')]).unlink()
```

Or via SQL:
```sql
DELETE FROM ir_attachment WHERE name LIKE 'web.assets_%';
```

Then restart Odoo.

### Method 5: Upgrade Module
```bash
./odoo-bin -u school_dashboard -d your_database
```

## Verify It's Working

After clearing cache, check:

1. Open browser console (F12)
2. Go to **School → Dashboard → Main Dashboard**
3. You should see the dashboard load
4. Check console for any errors
5. Look for: "Loading dashboard data..." message

## If Still Not Working

1. Check browser console for errors
2. Verify files exist:
   - `custom_addons/school_dashboard/static/src/js/dashboard.js`
   - `custom_addons/school_dashboard/static/src/xml/dashboard.xml`
   - `custom_addons/school_dashboard/static/src/css/dashboard.css`

3. Check Network tab in DevTools:
   - Look for `dashboard.js` being loaded
   - Check if Chart.js CDN loads

4. Verify module is installed:
   - Go to Apps
   - Search "School Dashboard"
   - Should show "Installed"

## Quick Test

Open browser console and type:
```javascript
odoo.loader.modules.get('@school_dashboard/static/src/js/dashboard')
```

If it returns `undefined`, the module isn't loaded.

## Force Reload Everything

Add this to your URL:
```
http://localhost:8080/web?debug=assets
```

This forces Odoo to:
- Reload all JavaScript
- Rebuild all assets
- Skip cache

## Common Issues

### Issue: "Cannot find key in registry"
**Cause**: JavaScript not loaded
**Fix**: Clear cache using Method 1 above

### Issue: Chart.js not defined
**Cause**: CDN blocked or not loaded
**Fix**: Check internet connection or download Chart.js locally

### Issue: Template not found
**Cause**: XML template not loaded
**Fix**: Verify `dashboard.xml` exists and is in manifest

## Alternative: Use Classic Dashboard

If OWL dashboard still doesn't work, use the classic dashboard:

Navigate to: **School → Dashboard → Classic Dashboard**

This uses the traditional Odoo kanban view and doesn't require custom JavaScript.

---

**After following these steps, the dashboard should work!**
