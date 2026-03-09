# Parent Model Added to School Core

## Changes Made

### 1. New Model: `school.parent`
Created a complete parent/guardian model with the following features:

**Fields:**
- `name` - Parent/guardian name (required)
- `partner_id` - Link to res.partner
- `relation` - Relationship type (father/mother/guardian/other)
- `gender` - Gender selection
- `email` - Email address
- `phone` - Phone number
- `mobile` - Mobile number
- `occupation` - Job/occupation
- `company_name` - Employer name
- `address` - Full address
- `student_ids` - Many2many relationship with students
- `student_count` - Computed field for number of children
- `is_emergency_contact` - Boolean flag
- `user_id` - Portal user account (for portal access)
- `notes` - Additional notes

**Methods:**
- `_compute_student_count()` - Calculate number of children
- `action_view_students()` - Open list of children
- `create()` - Auto-create partner record if email provided
- `write()` - Sync changes to partner record

### 2. Updated Model: `school.student`
Changed parent relationship from `res.partner` to `school.parent`:

**Old:**
```python
parent_ids = fields.Many2many("res.partner", string="Guardians")
```

**New:**
```python
parent_ids = fields.Many2many(
    "school.parent",
    "school_student_parent_rel",
    "student_id",
    "parent_id",
    string="Parents/Guardians"
)
```

**Added Fields:**
- `parent_count` - Computed field for number of parents
- `email` - Student email
- `phone` - Student phone
- `address` - Student address

**Added Methods:**
- `_compute_parent_count()` - Calculate number of parents
- `action_view_parents()` - Open list of parents/guardians

### 3. New Views: `parent_views.xml`
Created complete CRUD views for parent model:

- **Tree View** - List of parents with key information
- **Form View** - Detailed parent form with:
  - Smart button to view children
  - Personal information section
  - Employment information section
  - Address section
  - Children tab (many2many widget)
  - Portal access tab
  - Notes tab
  - Chatter integration
- **Search View** - Filters for:
  - Fathers/Mothers/Guardians
  - Emergency contacts
  - Portal access
  - Archived records
  - Group by relation/gender
- **Action** - Window action to open parent views
- **Menu Item** - Added to School menu

### 4. Updated Views: `student_views.xml`
Enhanced student form view:

- Added smart button to view parents (shows count)
- Updated Parents/Guardians tab with proper many2many widget
- Shows parent name, relation, phone, email, emergency contact flag
- Added email, phone, address fields to student form

### 5. Updated Files

**Modified:**
- `custom_addons/school_core/models/__init__.py` - Added parent import
- `custom_addons/school_core/models/student.py` - Updated parent relationship
- `custom_addons/school_core/views/student_views.xml` - Enhanced parent display
- `custom_addons/school_core/__manifest__.py` - Added parent_views.xml
- `custom_addons/school_core/security/ir.model.access.csv` - Added parent access rights

**Created:**
- `custom_addons/school_core/models/parent.py` - New parent model
- `custom_addons/school_core/views/parent_views.xml` - Parent views

### 6. Database Relationship

**Many2many Relationship:**
- Table: `school_student_parent_rel`
- Columns: `student_id`, `parent_id`
- Allows multiple parents per student
- Allows multiple students per parent (siblings)

**Benefits:**
- Proper data modeling for family relationships
- Support for single parents, guardians, multiple parents
- Easy to track siblings (students with same parent)
- Portal access management per parent
- Emergency contact designation

## Migration from Old Structure

If you have existing data with `parent_ids` as `res.partner`:

### Option 1: Manual Migration
1. Create `school.parent` records from existing `res.partner` guardians
2. Link them to students via the new many2many relationship
3. Clean up old `parent_ids` data

### Option 2: Migration Script
```python
# Run in Odoo shell
env = api.Environment(cr, SUPERUSER_ID, {})

# Get all students with old parent_ids (res.partner)
students = env['school.student'].search([])

for student in students:
    # This will fail because parent_ids now expects school.parent
    # You need to create school.parent records first
    pass

# Create parent records from res.partner
partners = env['res.partner'].search([
    ('id', 'in', students.mapped('parent_ids').ids)
])

for partner in partners:
    parent = env['school.parent'].create({
        'name': partner.name,
        'email': partner.email,
        'phone': partner.phone,
        'mobile': partner.mobile,
        'partner_id': partner.id,
        'relation': 'guardian',  # Default, update manually
    })
    
    # Link to students
    students_to_link = students.filtered(
        lambda s: partner.id in s.parent_ids.ids
    )
    parent.student_ids = [(6, 0, students_to_link.ids)]
```

## Usage Examples

### Create a Parent
```python
parent = env['school.parent'].create({
    'name': 'John Doe',
    'relation': 'father',
    'email': 'john.doe@example.com',
    'phone': '+1234567890',
    'is_emergency_contact': True,
})
```

### Link Parent to Student
```python
student = env['school.student'].browse(1)
parent = env['school.parent'].browse(1)

# Add parent to student
student.parent_ids = [(4, parent.id)]

# Or add student to parent
parent.student_ids = [(4, student.id)]
```

### Find Siblings
```python
student = env['school.student'].browse(1)

# Get all parents
parents = student.parent_ids

# Get all children of these parents (including the student)
all_children = parents.mapped('student_ids')

# Get siblings (exclude the student)
siblings = all_children - student
```

### Grant Portal Access
```python
parent = env['school.parent'].browse(1)

# This will be available after installing school_portal module
parent.action_grant_portal_access()
```

## Benefits of New Structure

1. **Proper Data Model** - Dedicated parent model instead of generic partner
2. **Rich Information** - Store parent-specific data (relation, occupation, emergency contact)
3. **Portal Integration** - Easy portal access management
4. **Sibling Support** - Natural sibling relationships through shared parents
5. **Emergency Contacts** - Flag parents as emergency contacts
6. **Better Reporting** - Query parent data separately from general contacts
7. **Extensibility** - Easy to add parent-specific features (meetings, communications, etc.)

## Next Steps

1. **Upgrade school_core module** to apply changes
2. **Migrate existing data** if you have old parent_ids
3. **Create parent records** for all students
4. **Install school_portal module** to enable parent portal access
5. **Grant portal access** to parents who need it

## Compatibility

- ✅ Compatible with school_academic module
- ✅ Compatible with school_fees module
- ✅ Compatible with school_dashboard module
- ✅ Compatible with school_portal module (updated to use school.parent)

## Notes

- The old `parent_ids` field pointing to `res.partner` has been replaced
- You may need to update any custom code that references the old structure
- The `partner_id` field on parent model maintains link to res.partner for compatibility
- Portal access is managed through the `user_id` field on parent model
