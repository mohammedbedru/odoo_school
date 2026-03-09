# Frozen Grades - Preventing Auto-Update on Student Promotion

## Problem

When a student is promoted to a new section, the report card was automatically updating:
1. **Section ID** was changing (because it was a related field)
2. **Grades were recalculating** (because they were computed fields)

This is incorrect because historical report cards should remain frozen and not change when students are promoted.

## Solution

Changed all dynamic fields to static fields that are calculated once and then frozen.

### Changes Made

#### 1. Section ID - No Longer Related Field

**Before:**
```python
section_id = fields.Many2one(related="student_id.section_id", store=True)
```

**After:**
```python
section_id = fields.Many2one("school.section", store=True)

@api.onchange("student_id")
def _onchange_student_id(self):
    if self.student_id:
        self.section_id = self.student_id.section_id
    else:
        self.section_id = False
```

**Result:** Section is copied from student when report card is created, but doesn't update when student is promoted.

#### 2. Grade Fields - No Longer Computed

**Before:**
```python
total_mark = fields.Float(compute="_compute_total_and_grade", store=True)
percentage = fields.Float(compute="_compute_total_and_grade", store=True)
grade = fields.Char(compute="_compute_total_and_grade", store=True)
```

**After:**
```python
total_mark = fields.Float(string="Total Marks", readonly=True)
percentage = fields.Float(string="Percentage", readonly=True)
grade = fields.Char(string="Grade", readonly=True)
```

**Result:** Values are calculated once when marks are entered and never recalculate.

#### 3. Calculation Triggers

Grades are now calculated only in these scenarios:

1. **On Create:** When a new line is created
2. **On Write:** When marks are updated AND report is in draft state
3. **On Fetch Marks:** When "Fetch Marks" button is clicked
4. **On Confirm/Publish:** Final calculation before freezing

**After publishing, grades NEVER recalculate.**

#### 4. Force Save in Views

Added `force_save="1"` to ensure readonly fields persist:

```xml
<field name="section_id" readonly="1" force_save="1"/>
<field name="total" force_save="1"/>
<field name="average" force_save="1"/>
<field name="total_mark" readonly="1" force_save="1"/>
<field name="percentage" readonly="1" force_save="1"/>
<field name="grade" readonly="1" force_save="1"/>
```

## How It Works Now

### Scenario 1: Creating Report Card

1. User selects student
2. Section is copied from student's current section
3. User clicks "Fetch Marks"
4. Marks are pulled from exams
5. Grades are calculated and saved
6. Total and average are calculated and saved

### Scenario 2: Manual Entry

1. User adds subject line
2. User enters marks (25/30, 45/50)
3. On save, grades calculate automatically
4. Values are stored in database
5. Parent report card totals update

### Scenario 3: Student Promotion

**Before Fix:**
```
Student: John Doe
Section: Grade 10-A (at time of report)
Grade: B

[Student promoted to Grade 11-A]

Report card updates:
Section: Grade 11-A ❌ WRONG!
Grades recalculate ❌ WRONG!
```

**After Fix:**
```
Student: John Doe
Section: Grade 10-A (frozen)
Grade: B (frozen)

[Student promoted to Grade 11-A]

Report card remains:
Section: Grade 10-A ✓ CORRECT!
Grade: B ✓ CORRECT!
```

### Scenario 4: Editing Published Report

When report is published:
- All fields become readonly
- Grades are frozen
- Even if marks are somehow changed, grades won't recalculate
- Historical accuracy is preserved

## State-Based Protection

```python
def write(self, vals):
    result = super().write(vals)
    mark_fields = ['quiz_mark', 'quiz_max', 'mid_mark', 'mid_max', 
                   'final_mark', 'final_max', 'assignment_mark', 'assignment_max']
    if any(field in vals for field in mark_fields):
        for record in self:
            if record.report_id.state == 'draft':  # Only in draft!
                record._compute_grade_on_save()
                record.report_id._calculate_totals()
    return result
```

**Protection:**
- Draft: Grades can recalculate when marks change
- Confirmed: Grades are frozen
- Published: Grades are frozen

## Database Storage

All values are stored directly in the database:

```sql
-- Report Card Line
UPDATE school_report_card_line 
SET total_mark = 70.0, 
    total_max = 80.0, 
    percentage = 87.5, 
    grade = 'B'
WHERE id = 123;

-- Report Card Header
UPDATE school_report_card 
SET total = 394.0, 
    average = 87.7
WHERE id = 456;
```

No computed fields = No automatic recalculation.

## Benefits

1. ✓ **Historical Accuracy**: Report cards reflect the student's performance at that time
2. ✓ **Section Preservation**: Shows which section the student was in during that term
3. ✓ **Grade Stability**: Grades don't change when grading scale is updated
4. ✓ **Audit Trail**: Complete history of student's academic journey
5. ✓ **Performance**: No unnecessary recalculations on every read
6. ✓ **Data Integrity**: Published reports are truly frozen

## Testing

Test these scenarios after upgrade:

### Test 1: Create and Publish Report
1. Create report card for student in Grade 10-A
2. Add marks: Math 25/30, Science 45/50
3. Verify grades calculate correctly
4. Publish report
5. Verify total and average are saved

### Test 2: Student Promotion
1. Open published report card
2. Note: Section = Grade 10-A, Grade = B
3. Promote student to Grade 11-A
4. Reopen same report card
5. Verify: Section still shows Grade 10-A ✓
6. Verify: Grade still shows B ✓

### Test 3: Edit Draft Report
1. Create draft report card
2. Add marks
3. Verify grades calculate
4. Change marks
5. Verify grades recalculate
6. Publish report
7. Try to change marks (should be readonly)

### Test 4: Fetch Marks
1. Create report card
2. Click "Fetch Marks"
3. Verify marks populate
4. Verify grades calculate
5. Verify totals calculate
6. Publish
7. Verify all values are frozen

## Migration Notes

If you have existing report cards:

1. **Grades may be empty** - Old computed fields won't have stored values
2. **Solution:** For each report card in draft state:
   - Open the report
   - Click "Fetch Marks" or manually save
   - Grades will calculate and save
3. **Published reports:** May need to recalculate once:
   - Set to draft temporarily
   - Save to trigger calculation
   - Publish again

Or run this SQL to recalculate all:

```sql
-- This would need to be done via Python script
-- to properly calculate grades for existing records
```

## Upgrade Instructions

```bash
# 1. Backup database
pg_dump your_database > backup_before_frozen_grades.sql

# 2. Upgrade module
./odoo-bin -u school_academic -d your_database

# 3. Test with sample data
# 4. Verify existing report cards
# 5. Recalculate any empty grades if needed
```
