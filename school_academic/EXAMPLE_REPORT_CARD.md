# Example Report Card - Before and After Fix

## Scenario

A student takes the following exams in Term 1:

**Mathematics:**
- Quiz: 25 out of 30 marks
- Midterm: 45 out of 50 marks

**Science:**
- Quiz: 18 out of 20 marks
- Final: 88 out of 100 marks

**English:**
- Midterm: 78 out of 100 marks
- Final: 92 out of 100 marks
- Assignment: 48 out of 50 marks

---

## BEFORE FIX (Incorrect)

### Mathematics
```
Quiz: 25 (assumed /100)
Midterm: 45 (assumed /100)
Total: 70
Max Assumed: 200 (2 exams × 100)
Percentage: 70/200 = 35%
Grade: F ❌ WRONG!
```

### Science
```
Quiz: 18 (assumed /100)
Final: 88 (assumed /100)
Total: 106
Max Assumed: 200 (2 exams × 100)
Percentage: 106/200 = 53%
Grade: D ❌ WRONG!
```

### English
```
Midterm: 78 (assumed /100)
Final: 92 (assumed /100)
Assignment: 48 (assumed /100)
Total: 218
Max Assumed: 300 (3 exams × 100)
Percentage: 218/300 = 72.7%
Grade: C ❌ WRONG!
```

**Overall Average: 53.6% (F)** ❌ WRONG!

---

## AFTER FIX (Correct)

### Mathematics
```
Quiz: 25/30 = 83.3%
Midterm: 45/50 = 90%
Total: 70/80
Percentage: 70/80 = 87.5%
Grade: B ✓ CORRECT!
```

### Science
```
Quiz: 18/20 = 90%
Final: 88/100 = 88%
Total: 106/120
Percentage: 106/120 = 88.3%
Grade: B ✓ CORRECT!
```

### English
```
Midterm: 78/100 = 78%
Final: 92/100 = 92%
Assignment: 48/50 = 96%
Total: 218/250
Percentage: 218/250 = 87.2%
Grade: B ✓ CORRECT!
```

**Overall Average: 87.7% (B)** ✓ CORRECT!

---

## Report Card Output (After Fix)

```
╔════════════════════════════════════════════════════════════════════════════╗
║                      ACADEMIC PROGRESS REPORT                              ║
║                         2024-2025 — Term 1                                 ║
╠════════════════════════════════════════════════════════════════════════════╣
║ Student: John Doe                    Grade/Section: Grade 10 - Section A  ║
║ Student ID: STU001                   Status: Published                     ║
╠════════════════════════════════════════════════════════════════════════════╣
║                        Subject Performance                                 ║
╠═══════════╤═══════════╤═══════╤═══════╤═══════╤═══════╤═══════╤═════╤═════╣
║ Subject   │ Instructor│ Quiz  │ Mid   │ Final │ Assign│ Total │  %  │Grade║
╠═══════════╪═══════════╪═══════╪═══════╪═══════╪═══════╪═══════╪═════╪═════╣
║Mathematics│ Mr. Smith │ 25/30 │ 45/50 │   -   │   -   │ 70/80 │87.5%│  B  ║
╠═══════════╪═══════════╪═══════╪═══════╪═══════╪═══════╪═══════╪═════╪═════╣
║ Science   │ Ms. Jones │ 18/20 │   -   │88/100 │   -   │106/120│88.3%│  B  ║
╠═══════════╪═══════════╪═══════╪═══════╪═══════╪═══════╪═══════╪═════╪═════╣
║ English   │ Mr. Brown │   -   │78/100 │92/100 │ 48/50 │218/250│87.2%│  B  ║
╠═══════════╧═══════════╧═══════╧═══════╧═══════╧═══════╪═══════╪═════╧═════╣
║                                      Overall Total:    │  394  │ 87.7%     ║
╚════════════════════════════════════════════════════════╧═══════╧═══════════╝

Grading Scale: A (90-100%) | B (75-89%) | C (60-74%) | D (50-59%) | F (<50%)

Overall Average: 87.7%
```

---

## Key Differences

| Aspect | Before Fix | After Fix |
|--------|-----------|-----------|
| **Max Marks** | Assumed 100 for all | Uses actual max marks |
| **Math Grade** | F (35%) | B (87.5%) |
| **Science Grade** | D (53%) | B (88.3%) |
| **English Grade** | C (72.7%) | B (87.2%) |
| **Overall** | F (53.6%) | B (87.7%) |
| **Display** | Just marks | Marks with max (25/30) |
| **Accuracy** | ❌ Incorrect | ✓ Correct |

---

## How It Works Now

### 1. Fetch Marks from Exams
When you click "Fetch Marks":
- System finds all published exams for the student
- For each exam, it pulls:
  - The mark obtained (e.g., 25)
  - The max mark (e.g., 30)
  - The exam type (quiz, mid, final, assignment)
- Groups by subject
- Creates one line per subject with all exam types

### 2. Automatic Calculation
For each subject line:
```python
# Example: Mathematics
quiz_mark = 25, quiz_max = 30
mid_mark = 45, mid_max = 50

# Calculate totals
total_mark = 25 + 45 = 70
total_max = 30 + 50 = 80  # Only counts exams taken

# Calculate percentage
percentage = (70 / 80) × 100 = 87.5%

# Assign grade
if percentage >= 90: grade = "A"
elif percentage >= 75: grade = "B"  ← This one!
elif percentage >= 60: grade = "C"
elif percentage >= 50: grade = "D"
else: grade = "F"
```

### 3. Overall Average
```python
# Calculate average of subject percentages
subjects = [87.5%, 88.3%, 87.2%]
overall_average = (87.5 + 88.3 + 87.2) / 3 = 87.7%
```

---

## Manual Entry Example

If entering marks manually:

1. **Add subject line**: Mathematics
2. **Enter marks**:
   - Quiz Mark: 25
   - Quiz Max: 30
   - Midterm Mark: 45
   - Midterm Max: 50
3. **System calculates automatically**:
   - Total: 70/80
   - Percentage: 87.5%
   - Grade: B

**Note:** Max mark fields are hidden by default. Enable them from column options if needed.

---

## Benefits of the Fix

1. ✓ **Accurate Grading**: Reflects actual student performance
2. ✓ **Flexible Exams**: Supports any max mark value (20, 30, 50, 100, etc.)
3. ✓ **Transparent**: Shows both obtained and max marks (25/30)
4. ✓ **Automatic**: Calculates percentage and grade automatically
5. ✓ **Fair**: Students aren't penalized for exams with different max marks
6. ✓ **Professional**: Report card looks like real school reports

---

## Testing Your Report Cards

After upgrading, test with these cases:

**Test 1: All 100-based (should still work)**
- Quiz: 85/100, Mid: 78/100, Final: 92/100
- Expected: 255/300 = 85% = B ✓

**Test 2: Mixed max marks**
- Quiz: 25/30, Mid: 45/50
- Expected: 70/80 = 87.5% = B ✓

**Test 3: Single exam**
- Final: 92/100
- Expected: 92/100 = 92% = A ✓

**Test 4: All different**
- Quiz: 18/20, Mid: 45/50, Final: 88/100, Assignment: 48/50
- Expected: 199/220 = 90.5% = A ✓
