# Grading Calculation Fix

## Problem

Student scored 25/30 and 45/50 but received grade "F" in the report card.

**Root Cause:** The system was assuming all exams were out of 100 marks, so:
- 25 + 45 = 70 total marks
- Assumed max: 200 (2 exams × 100)
- Calculated percentage: 70/200 = 35%
- Grade: F (below 50%)

**Actual Performance:**
- Quiz: 25/30 = 83.3%
- Midterm: 45/50 = 90%
- Actual percentage: (25+45)/(30+50) = 70/80 = 87.5%
- Should be: Grade B

## Solution

Added support for variable maximum marks per exam type.

### Changes Made

1. **Added Max Mark Fields** (`models/report_card.py`):
   - `quiz_max` (default: 100)
   - `mid_max` (default: 100)
   - `final_max` (default: 100)
   - `assignment_max` (default: 100)

2. **Added Computed Fields**:
   - `total_max`: Sum of max marks for exams taken
   - `percentage`: Actual percentage (total_mark / total_max × 100)

3. **Updated Grade Calculation**:
   ```python
   # Old (wrong)
   max_possible = count_of_exams × 100
   percentage = total_marks / max_possible × 100
   
   # New (correct)
   max_possible = quiz_max + mid_max + final_max + assignment_max (only if taken)
   percentage = total_marks / max_possible × 100
   ```

4. **Updated Fetch Marks**:
   - Now pulls `max_mark` from each exam
   - Stores it in the appropriate max field

5. **Updated Report Template**:
   - Shows marks as "25/30" instead of just "25"
   - Added percentage column
   - Shows total as "70/80" format

## Example

### Before Fix:
```
Subject | Quiz | Mid  | Total | Grade
Math    | 25   | 45   | 70    | F (35%)
```
System thought: 70 out of 200 possible = 35% = F

### After Fix:
```
Subject | Quiz  | Mid   | Total | %     | Grade
Math    | 25/30 | 45/50 | 70/80 | 87.5% | B
```
System correctly calculates: 70 out of 80 possible = 87.5% = B

## Grading Scale

Grades are assigned based on **actual percentage**:
- **A**: 90-100%
- **B**: 75-89%
- **C**: 60-74%
- **D**: 50-59%
- **F**: Below 50%

## Usage

### Automatic (Recommended)

When using "Fetch Marks" button:
- System automatically pulls max marks from exams
- Calculates percentage correctly
- Assigns proper grade

### Manual Entry

When entering marks manually:
1. Enter the mark obtained (e.g., 25)
2. Enter the max mark (e.g., 30)
3. System calculates percentage automatically
4. Grade is assigned based on percentage

**Example:**
- Quiz Mark: 25
- Quiz Max: 30
- System calculates: 25/30 = 83.3%

### View Max Marks in Form

Max mark fields are hidden by default (to keep the view clean).

To show them:
1. Open report card form
2. Click on column options (⋮) in the list
3. Enable: "Quiz Max", "Mid Max", "Final Max", "Assignment Max"

## Migration

If you have existing report cards with incorrect grades:

1. **Option A: Regenerate**
   - Delete existing report cards
   - Use "Fetch Marks" to regenerate
   - Max marks will be pulled automatically

2. **Option B: Manual Fix**
   - Open each report card
   - Show max mark columns
   - Enter correct max marks for each exam
   - Grades will recalculate automatically

## Testing

Test with these scenarios:

**Test 1: Different Max Marks**
- Quiz: 25/30
- Midterm: 45/50
- Expected: 70/80 = 87.5% = Grade B ✓

**Test 2: All 100-based**
- Quiz: 85/100
- Midterm: 78/100
- Final: 92/100
- Expected: 255/300 = 85% = Grade B ✓

**Test 3: Mixed**
- Quiz: 18/20
- Midterm: 45/50
- Final: 88/100
- Expected: 151/170 = 88.8% = Grade B ✓

**Test 4: Single Exam**
- Final: 92/100
- Expected: 92/100 = 92% = Grade A ✓

## Upgrade Instructions

1. **Upgrade the module:**
   ```bash
   ./odoo-bin -u school_academic -d your_database
   ```

2. **Existing report cards:**
   - Old report cards will have max marks = 0
   - Grades may show as blank
   - Regenerate or manually enter max marks

3. **New report cards:**
   - Use "Fetch Marks" button
   - Max marks pulled automatically from exams
   - Grades calculate correctly

## Notes

- Default max mark is 100 for backward compatibility
- Max marks are stored per exam type per subject
- Percentage is always calculated from actual max marks
- Overall average is the average of subject percentages (not raw marks)
