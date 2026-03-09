# Quick Upgrade Guide - Realistic Report Card Format

## What Changed?

The report card system has been completely redesigned to match **real school report cards**:

**Before:** Multiple rows per subject (one for each exam type)
```
Math - Quiz: 85
Math - Midterm: 78
Math - Final: 92
```

**After:** One row per subject with columns for each exam type
```
Subject | Quiz | Midterm | Final | Assignment | Total | Grade
Math    | 85   | 78      | 92    | -          | 255   | B
```

## Steps to Apply Changes

### 1. Backup Your Database (IMPORTANT!)

```bash
# Create a backup before upgrading
pg_dump your_database_name > backup_before_report_card_upgrade.sql
```

This is a structural change - backup is essential!

### 2. Restart Odoo and Upgrade Module

```bash
# Stop Odoo if running
# Then restart with upgrade flag
./odoo-bin -u school_academic -d your_database_name
```

Or from Odoo UI:
1. Go to Apps menu (enable Developer Mode)
2. Remove "Apps" filter
3. Search for "School Academic"
4. Click "Upgrade"

### 3. Handle Existing Data

**If you have existing report cards:**

#### Option A: Fresh Start (Recommended)
1. Delete all existing report cards
2. Recreate them using "Fetch Marks" button
3. New format will be applied automatically

#### Option B: Keep Old Data
- Old report cards will remain in old format
- Create new report cards in new format
- Gradually phase out old ones

### 4. Verify Changes

After upgrade, check:

**Form View:**
- Report card lines show: Subject | Teacher | Quiz | Mid | Final | Assignment | Total | Grade
- Total and Grade are read-only (auto-calculated)
- You can edit individual exam marks

**Report PDF:**
- Each subject appears as one row
- Columns for Quiz, Midterm, Final, Assignment
- Total and Grade calculated automatically
- Professional layout with signatures section

### 5. Test the New Features

**Test Case 1: Create New Report Card**
1. Go to Academic → Report Cards → Create
2. Select: Student, Term, Academic Year
3. Click "Fetch Marks"
4. Verify marks populate in correct columns
5. Check Total and Grade calculate correctly

**Test Case 2: Manual Entry**
1. Create new report card
2. Add subject line manually
3. Enter: Quiz=85, Midterm=78, Final=92
4. Verify: Total=255, Grade=B (85%)

**Test Case 3: Print Report**
1. Open any report card
2. Click "Print Report Card"
3. Verify PDF shows proper table format
4. Check all columns align correctly

## Understanding the New Format

### Data Structure

**Each report card line contains:**
- Subject (e.g., Mathematics)
- Teacher (e.g., Mr. Smith)
- Quiz Mark (0-100)
- Midterm Mark (0-100)
- Final Mark (0-100)
- Assignment Mark (0-100)
- **Total** (auto-calculated sum)
- **Grade** (auto-calculated: A, B, C, D, F)
- Remark (optional text)

### Grade Calculation

```
Step 1: Sum all marks
Total = Quiz + Midterm + Final + Assignment

Step 2: Calculate max possible
Max = 100 × (number of exams with marks > 0)

Step 3: Calculate percentage
Percentage = (Total / Max) × 100

Step 4: Assign grade
A: 90-100%
B: 75-89%
C: 60-74%
D: 50-59%
F: Below 50%
```

**Example:**
- Quiz: 85, Midterm: 78, Final: 92, Assignment: 0 (not taken)
- Total: 255
- Max: 300 (3 exams taken)
- Percentage: 85%
- Grade: B

### "Fetch Marks" Behavior

When you click "Fetch Marks":
1. System finds all published exams for the student's section and term
2. Groups exams by subject
3. Maps each exam type to its column:
   - exam_type="quiz" → quiz_mark
   - exam_type="mid" → mid_mark
   - exam_type="final" → final_mark
   - exam_type="assignment" → assignment_mark
4. Creates one line per subject
5. Total and Grade calculate automatically

## Troubleshooting

### Issue: "Duplicate subject in report card"
**Cause:** Trying to add same subject twice
**Solution:** Each subject can only appear once per report card. Edit the existing line instead.

### Issue: Grade not calculating
**Cause:** All exam marks are 0
**Solution:** Enter at least one exam mark > 0

### Issue: Total seems wrong
**Cause:** Expecting weighted average, but system uses simple sum
**Solution:** This is by design. Total = sum of all marks. Grade is based on percentage.

### Issue: Old report cards look broken
**Cause:** Old data structure doesn't match new format
**Solution:** 
- Delete old report cards
- Regenerate using "Fetch Marks"
- Or keep old ones as archive and create new ones

### Issue: "Fetch Marks" not working
**Verify:**
- Exams are in "Published" state
- Exams have exam_type set (quiz, mid, final, assignment)
- Exams match the report card's term and academic year
- Student has marks entered in those exams

## Rollback (if needed)

If you need to revert:

1. **Restore database backup:**
   ```bash
   dropdb your_database_name
   createdb your_database_name
   psql your_database_name < backup_before_report_card_upgrade.sql
   ```

2. **Checkout previous git commit:**
   ```bash
   git log --oneline  # Find commit before changes
   git checkout <commit-hash>
   ```

3. **Restart Odoo:**
   ```bash
   ./odoo-bin -d your_database_name
   ```

## Next Steps

1. ✅ Upgrade module
2. ✅ Test with sample data
3. ✅ Train staff on new format
4. ✅ Migrate or recreate existing report cards
5. ✅ Print sample reports for review
6. ✅ Roll out to production

## Support

For detailed documentation, see: `REPORT_CARD_CHANGES.md`

For questions or issues, contact your system administrator.
