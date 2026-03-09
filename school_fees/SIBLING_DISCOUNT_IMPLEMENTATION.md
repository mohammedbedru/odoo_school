# Sibling Discount Implementation

## Overview
Automatic sibling discount feature that applies discounts to students who have siblings enrolled in the same academic year.

## How It Works

### Sibling Detection
The system automatically detects siblings by:
1. Checking if students share at least one parent/guardian (via `parent_ids` field)
2. Verifying siblings are enrolled in the same academic year
3. Ensuring siblings have active status (`enrolled` or `active`)

### Discount Calculation
Discount percentage is based on the number of siblings:
- **2 siblings (1 other sibling)**: 10% discount
- **3 siblings (2 other siblings)**: 15% discount
- **4+ siblings (3+ other siblings)**: 20% discount

### Configuration
Discount rates can be customized via System Parameters:
- `school_fees.sibling_discount_2` - Discount for 2 siblings (default: 10.0)
- `school_fees.sibling_discount_3` - Discount for 3 siblings (default: 15.0)
- `school_fees.sibling_discount_4_plus` - Discount for 4+ siblings (default: 20.0)

## Fields Added

### Student Fee Model (`school.student.fee`)

| Field | Type | Description |
|-------|------|-------------|
| `apply_sibling_discount` | Boolean | Enable/disable sibling discount for this fee |
| `has_sibling_discount` | Boolean (computed) | Whether student qualifies for sibling discount |
| `sibling_count` | Integer (computed) | Number of siblings found |
| `sibling_discount_percent` | Float (computed) | Discount percentage applied |
| `sibling_discount_amount` | Monetary (computed) | Discount amount in currency |

## Invoice Generation
When generating an invoice, if sibling discount applies:
- A separate invoice line is added with negative amount
- Product: "Sibling Discount" (`product_sibling_discount`)
- Description includes sibling count and discount percentage
- Example: "Sibling Discount (3 siblings - 15%)"

## Example Scenarios

### Scenario 1: Two Siblings
**Setup:**
- Parent: John Doe
- Student 1: Alice (Grade 5) - Fee: $1000
- Student 2: Bob (Grade 3) - Fee: $800

**Result:**
- Alice: $1000 - $100 (10%) = $900
- Bob: $800 - $80 (10%) = $720
- Total savings: $180

### Scenario 2: Three Siblings
**Setup:**
- Parent: Jane Smith
- Student 1: Charlie (Grade 6) - Fee: $1000
- Student 2: Diana (Grade 4) - Fee: $800
- Student 3: Emma (Grade 2) - Fee: $600

**Result:**
- Charlie: $1000 - $150 (15%) = $850
- Diana: $800 - $120 (15%) = $680
- Emma: $600 - $90 (15%) = $510
- Total savings: $360

### Scenario 3: Disabled Discount
**Setup:**
- Student with siblings but `apply_sibling_discount = False`

**Result:**
- No discount applied
- Full fee amount charged

## Usage

### Automatic Application
1. Create student fee record
2. System automatically detects siblings
3. Discount is calculated and applied
4. Generate invoice - discount line is included

### Manual Control
To disable sibling discount for specific student:
1. Open student fee record
2. Uncheck "Apply Sibling Discount"
3. Discount will be removed from calculation

### Viewing Sibling Information
In student fee form view:
- "Sibling Discount" section shows:
  - Apply Sibling Discount checkbox
  - Has Sibling Discount indicator
  - Number of siblings
  - Discount percentage
  - Discount amount

### Filtering
Use search filters to find:
- "With Sibling Discount" - All fees with sibling discount applied
- Group by student to see family discounts together

## Technical Details

### Computation Dependencies
```python
@api.depends('student_id', 'student_id.parent_ids', 'apply_sibling_discount', 'academic_year_id')
def _compute_sibling_discount(self):
    # Finds siblings and calculates discount percentage
```

### Amount Calculation
```python
@api.depends("structure_id.total_amount", "discount_type", "discount_value", 
             "scholarship_id", "sibling_discount_percent")
def _compute_amount_total(self):
    # Applies all discounts including sibling discount
    amount_total = base_amount - discount - scholarship - sibling_discount
```

### Invoice Line Generation
```python
if rec.sibling_discount_amount > 0:
    sibling_product = self.env.ref('school_fees.product_sibling_discount')
    sibling_name = f"Sibling Discount ({rec.sibling_count + 1} siblings - {rec.sibling_discount_percent}%)"
    invoice_lines.append((0, 0, {
        "product_id": sibling_product.id,
        "name": sibling_name,
        "quantity": 1,
        "price_unit": -rec.sibling_discount_amount,
    }))
```

## Product Configuration
Product: `school_fees.product_sibling_discount`
- Name: Sibling Discount
- Type: Service
- Category: All
- Description: Automatic discount for students with siblings enrolled

## Integration with Other Discounts
Sibling discount works alongside:
- Manual discounts (percentage/fixed)
- Scholarship discounts
- All discounts are cumulative and applied to base amount

**Calculation Order:**
1. Base amount from fee structure
2. Subtract manual discount
3. Subtract scholarship discount
4. Subtract sibling discount
5. Final amount = base - all discounts

## Reporting
List view shows:
- Sibling discount amount (optional column)
- Has sibling discount indicator (optional column)

Filter by:
- Students with sibling discount
- Group by student to see family totals

## Maintenance

### Updating Discount Rates
1. Go to Settings > Technical > Parameters > System Parameters
2. Add/update parameters:
   - `school_fees.sibling_discount_2`
   - `school_fees.sibling_discount_3`
   - `school_fees.sibling_discount_4_plus`
3. Changes apply to new fee calculations immediately

### Troubleshooting

**Sibling not detected:**
- Verify students share at least one parent in `parent_ids`
- Check both students are in same academic year
- Ensure sibling status is 'enrolled' or 'active'

**Discount not applied:**
- Check "Apply Sibling Discount" is enabled
- Verify sibling count > 0
- Ensure fee is in draft state for recalculation

**Wrong discount percentage:**
- Check system parameters for discount rates
- Verify sibling count is correct
- Review discount calculation logic

## Future Enhancements
Potential improvements:
- Different discount rates per grade level
- Maximum discount cap per family
- Discount based on total family fees
- Sibling discount report/dashboard
- Email notification to parents about discount
