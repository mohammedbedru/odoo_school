# Sibling Discount - Testing Guide

## Prerequisites
1. Odoo 18 instance running
2. `school_fees` module installed and upgraded
3. At least one academic year created
4. At least one fee structure created
5. At least one parent/guardian contact created

## Test Scenario 1: Two Siblings (10% Discount)

### Setup
1. Create a parent contact:
   - Go to Contacts
   - Create: "John Smith"
   - Save

2. Create first student:
   - Go to School → Students
   - Create:
     - Name: "Alice Smith"
     - Grade: Grade 5
     - Section: A
     - Status: Active
     - Academic Year: 2024-2025
     - Guardians: Add "John Smith"
   - Save

3. Create second student:
   - Create:
     - Name: "Bob Smith"
     - Grade: Grade 3
     - Section: B
     - Status: Active
     - Academic Year: 2024-2025
     - Guardians: Add "John Smith"
   - Save

### Test Steps
1. Create fee for Alice:
   - Go to School Fees → Student Fees
   - Create:
     - Student: Alice Smith
     - Academic Year: 2024-2025
     - Term: Term 1
     - Fee Structure: Select one (e.g., 10,000)
     - Due Date: Set future date
   - Save

2. Verify sibling discount:
   - Check "Sibling Discount" section
   - ✅ "Has Sibling Discount" should be checked
   - ✅ "Number of Siblings" should show: 1
   - ✅ "Sibling Discount %" should show: 10.0
   - ✅ "Sibling Discount" amount should show: 1,000 (10% of 10,000)
   - ✅ "Amount Total" should show: 9,000

3. Create fee for Bob:
   - Create another fee for Bob Smith
   - Same academic year and term
   - Fee Structure: 8,000

4. Verify Bob's discount:
   - ✅ "Number of Siblings" should show: 1
   - ✅ "Sibling Discount %" should show: 10.0
   - ✅ "Sibling Discount" amount should show: 800 (10% of 8,000)
   - ✅ "Amount Total" should show: 7,200

5. Generate invoice for Alice:
   - Click "Generate Invoice"
   - Click "View Invoice"
   - Verify invoice lines:
     - ✅ Fee structure lines (positive amounts)
     - ✅ "Sibling Discount (2 siblings - 10%)" line with -1,000
     - ✅ Total matches: 9,000

### Expected Results
- Both students get 10% discount
- Alice saves: 1,000
- Bob saves: 800
- Total family savings: 1,800

---

## Test Scenario 2: Three Siblings (15% Discount)

### Setup
1. Use same parent "John Smith"
2. Create third student:
   - Name: "Charlie Smith"
   - Grade: Grade 1
   - Status: Active
   - Academic Year: 2024-2025
   - Guardians: Add "John Smith"

### Test Steps
1. Create fee for Charlie:
   - Fee Structure: 6,000
   - Save

2. Verify all three students:
   - Open Alice's fee → Edit
   - ✅ "Number of Siblings" should now show: 2
   - ✅ "Sibling Discount %" should now show: 15.0
   - ✅ "Sibling Discount" amount should update to: 1,500
   - ✅ "Amount Total" should update to: 8,500

3. Check Bob's fee:
   - ✅ "Number of Siblings": 2
   - ✅ "Sibling Discount %": 15.0
   - ✅ "Sibling Discount" amount: 1,200
   - ✅ "Amount Total": 6,800

4. Check Charlie's fee:
   - ✅ "Number of Siblings": 2
   - ✅ "Sibling Discount %": 15.0
   - ✅ "Sibling Discount" amount: 900
   - ✅ "Amount Total": 5,100

### Expected Results
- All three students get 15% discount
- Alice saves: 1,500
- Bob saves: 1,200
- Charlie saves: 900
- Total family savings: 3,600

---

## Test Scenario 3: Four Siblings (20% Discount)

### Setup
1. Create fourth student:
   - Name: "Diana Smith"
   - Grade: Kindergarten
   - Status: Active
   - Academic Year: 2024-2025
   - Guardians: Add "John Smith"

### Test Steps
1. Create fee for Diana:
   - Fee Structure: 5,000

2. Verify all four students now get 20% discount:
   - Alice: 10,000 - 2,000 = 8,000
   - Bob: 8,000 - 1,600 = 6,400
   - Charlie: 6,000 - 1,200 = 4,800
   - Diana: 5,000 - 1,000 = 4,000

### Expected Results
- All four students get 20% discount
- Total family savings: 5,800

---

## Test Scenario 4: Disable Sibling Discount

### Test Steps
1. Open Alice's fee
2. Uncheck "Apply Sibling Discount"
3. Save

### Expected Results
- ✅ "Has Sibling Discount" becomes unchecked
- ✅ "Sibling Discount" amount becomes 0
- ✅ "Amount Total" returns to full amount (10,000)
- ✅ Other siblings still have discount

---

## Test Scenario 5: Different Academic Years

### Setup
1. Create new academic year: 2025-2026
2. Promote Alice to new academic year
3. Keep Bob, Charlie, Diana in 2024-2025

### Test Steps
1. Create fee for Alice in 2025-2026:
   - Academic Year: 2025-2026
   - Save

### Expected Results
- ✅ Alice's new fee shows "Number of Siblings": 0
- ✅ No sibling discount applied (different academic year)
- ✅ Bob, Charlie, Diana still have discount among themselves

---

## Test Scenario 6: Inactive Sibling

### Test Steps
1. Open Bob's student record
2. Change Status to "Dropped"
3. Save
4. Open Alice's fee → Edit

### Expected Results
- ✅ "Number of Siblings" decreases by 1
- ✅ Discount percentage adjusts accordingly
- ✅ Amount recalculates

---

## Test Scenario 7: Multiple Parents

### Setup
1. Create second parent: "Jane Smith"
2. Add Jane to Alice and Bob's guardians
3. Create new student "Emma Jones" with only Jane as guardian

### Test Steps
1. Create fee for Emma
2. Verify sibling detection

### Expected Results
- ✅ Emma is detected as sibling of Alice and Bob (shares Jane)
- ✅ Discount applies correctly

---

## Test Scenario 8: Combined Discounts

### Test Steps
1. Open Alice's fee
2. Add manual discount:
   - Discount Type: Percentage
   - Discount Value: 5%
3. Add scholarship:
   - Create scholarship: "Merit Scholarship" (10%)
   - Apply to Alice's fee
4. Save

### Expected Results
- Base Amount: 10,000
- Manual Discount (5%): -500
- Scholarship (10%): -1,000
- Sibling Discount (15%): -1,500
- ✅ Final Amount: 7,000

---

## Test Scenario 9: Invoice Generation

### Test Steps
1. Open Alice's fee (with sibling discount)
2. Click "Generate Invoice"
3. Click "View Invoice"

### Expected Results
- ✅ Invoice has separate line for sibling discount
- ✅ Line description: "Sibling Discount (3 siblings - 15%)"
- ✅ Line amount: -1,500 (negative)
- ✅ Invoice total matches fee amount_total

---

## Test Scenario 10: List View and Filters

### Test Steps
1. Go to School Fees → Student Fees
2. Add optional columns:
   - Has Sibling Discount
   - Sibling Discount Amount
3. Apply filter: "With Sibling Discount"

### Expected Results
- ✅ Columns display correctly
- ✅ Filter shows only fees with sibling discount
- ✅ Values are accurate

---

## Configuration Testing

### Test Custom Discount Rates

1. Go to Settings → Technical → Parameters → System Parameters
2. Create/Update:
   - Key: `school_fees.sibling_discount_2`
   - Value: `12.0` (change from 10%)
3. Save
4. Open existing fee with 2 siblings → Edit

### Expected Results
- ✅ Discount percentage updates to 12%
- ✅ Amount recalculates automatically

---

## Edge Cases

### Test Case 1: No Parents
- Student with no guardians
- ✅ No sibling discount applied
- ✅ No errors

### Test Case 2: Same Parent, Different Names
- Students with same parent but different last names
- ✅ Siblings detected correctly
- ✅ Discount applies

### Test Case 3: Fee Already Invoiced
- Generate invoice first
- Then add sibling
- ✅ Existing invoice unchanged
- ✅ New fees get discount

### Test Case 4: Zero Fee Structure
- Fee structure with 0 amount
- ✅ Sibling discount calculates as 0
- ✅ No errors

---

## Performance Testing

### Large Family Test
1. Create 10 siblings with same parents
2. Create fees for all
3. Verify:
   - ✅ Calculation completes quickly
   - ✅ All get 20% discount (4+ tier)
   - ✅ No performance issues

---

## Troubleshooting Tests

### Issue: Sibling Not Detected

**Check:**
1. Both students have same parent in `parent_ids`
2. Both in same academic year
3. Both have status 'enrolled' or 'active'
4. "Apply Sibling Discount" is checked

### Issue: Wrong Discount Percentage

**Check:**
1. Sibling count is correct
2. System parameters are set correctly
3. Fee is in draft state (not invoiced)

### Issue: Discount Not on Invoice

**Check:**
1. Sibling discount product exists
2. Product ID: `school_fees.product_sibling_discount`
3. Invoice generated after discount applied

---

## Regression Testing

After any code changes, verify:
- [ ] Sibling detection still works
- [ ] Discount calculation is accurate
- [ ] Invoice generation includes discount
- [ ] Combined discounts work correctly
- [ ] No errors in logs
- [ ] Performance is acceptable

---

## Success Criteria

✅ All test scenarios pass
✅ No errors in Odoo logs
✅ Discounts calculate correctly
✅ Invoices show discount lines
✅ Combined discounts work
✅ Configuration changes apply
✅ Edge cases handled gracefully
✅ Performance is acceptable

---

## Test Data Cleanup

After testing:
```python
# Delete test fees
fees = env['school.student.fee'].search([('student_id.name', 'ilike', 'Smith')])
fees.unlink()

# Delete test students
students = env['school.student'].search([('name', 'ilike', 'Smith')])
students.unlink()

# Delete test parent
parent = env['res.partner'].search([('name', '=', 'John Smith')])
parent.unlink()
```

---

## Automated Testing (Optional)

Create unit tests in `tests/test_sibling_discount.py`:

```python
from odoo.tests import TransactionCase

class TestSiblingDiscount(TransactionCase):
    
    def setUp(self):
        super().setUp()
        # Setup test data
        
    def test_two_siblings_discount(self):
        # Test 10% discount for 2 siblings
        pass
        
    def test_three_siblings_discount(self):
        # Test 15% discount for 3 siblings
        pass
        
    def test_four_plus_siblings_discount(self):
        # Test 20% discount for 4+ siblings
        pass
        
    def test_disable_sibling_discount(self):
        # Test disabling discount
        pass
        
    def test_different_academic_years(self):
        # Test siblings in different years
        pass
```

Run tests:
```bash
./odoo-bin -d test_db -i school_fees --test-enable --stop-after-init
```

---

## Sign-Off

Tester: _______________
Date: _______________
Result: ☐ PASS  ☐ FAIL
Notes: _______________________________________________
