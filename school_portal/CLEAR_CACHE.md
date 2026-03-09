# Clear Cache Instructions

The portal is showing old cached templates. Follow these steps:

## 1. Upgrade the Module
```
Apps → School Portal → Upgrade
```

## 2. Clear Odoo Assets Cache
Go to Settings → Technical → Database Structure → Clear Assets Cache
Or visit: `/web/webclient/clear_cache`

## 3. Clear Browser Cache
- Chrome/Edge: Ctrl+Shift+Delete → Clear cached images and files
- Or hard refresh: Ctrl+F5 or Ctrl+Shift+R

## 4. Restart Odoo Server (if needed)
```bash
# Stop and start your Odoo service
```

## 5. Verify
After clearing cache, visit `/my/home` and check:
- No 404 errors for Font Awesome icons in console
- All 6 student portal cards should be visible
- Logs should show: `is_student=True`

## Quick Test
Open browser console (F12) and check for:
- ❌ No `/my/fa%20fa-graduation-cap` errors
- ✅ `<div id="portal_school_category">` element exists
- ✅ 6 cards visible for students

## If Still Not Working
1. Check if view is in database:
   ```sql
   SELECT * FROM ir_ui_view WHERE name = 'Portal My Home Menu - School';
   ```

2. Force view update:
   - Settings → Technical → User Interface → Views
   - Search for "Portal My Home Menu - School"
   - Delete the view
   - Upgrade module again
