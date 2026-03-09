# Discount Application Fix

## Problem

Discounts and scholarships were being calculated and shown in the `amount_total` field, but when the invoice was generated, it used the original fee structure amounts without applying the discounts. This meant:

- Student Fee shows: Amount Total = 7,000 (after 3,000 discount)
- Invoice shows: Amount Due = 10,000 (original amount) ❌

## Solution

Modified the `action_generate_invoice()` method to add discount and scholarship as separate invoice lines with negative amounts.

## How It Works Now

### Before Fix:
```python
# Invoice lines
Tuition Fee: 8,000
Books Fee: 2,000
-----------------
Total: 10,000  ❌ (discounts not applied)
```

### After Fix:
```python
# Invoice lines
Tuition Fee: 8,000
Books Fee: 2,000
Discount (10%): -1,000  ← Added
Scholarship (Merit): -2,000  ← Added
-----------------
Total: 7,000  ✓ (matches student fee amount_total)
```

## Implementation Details

### 1. Added Discount Products

Created two new service products:
- **Fee Discount** (`product_discount`): For manual discounts
- **Scholarship Discount** (`product_scholarship`): For scholarship discounts

These products are used to add discount lines to invoices.

### 2. Updated Invoice Generation

```python
def action_generate_invoice(self):
    # ... existing code ...
    
    # Add fee structure lines (original amounts)
    for line in rec.structure_id.line_ids:
        invoice_lines.append((0, 0, {
            "product_id": line.product_id.id,
            "name": line.product_id.name,
            "quantity": 1,
            "price_unit": line.amount,
        }))
    
    # Apply manual discount if exists
    if rec.discount_amount > 0:
        invoice_lines.append((0, 0, {
            "product_id": discount_product.id,
            "name": f"Discount ({rec.discount_type}: {rec.discount_value})",
            "quantity": 1,
            "price_unit": -rec.discount_amount,  # Negative!
        }))
    
    # Apply scholarship discount if exists
    if rec.scholarship_amount > 0:
        invoice_lines.append((0, 0, {
            "product_id": scholarship_product.id,
            "name": f"Scholarship: {rec.scholarship_id.name}",
            "quantity": 1,
            "price_unit": -rec.scholarship_amount,  # Negative!
        }))
```

### 3. Negative Amounts

The key is using **negative amounts** for discount lines:
- Regular fee lines: Positive amounts (e.g., +8,000)
- Discount lines: Negative amounts (e.g., -1,000)
- Invoice total: Sum of all lines (8,000 + 2,000 - 1,000 - 2,000 = 7,000)

## Example Scenarios

### Scenario 1: Manual Discount Only

**Student Fee:**
- Base Amount: 10,000
- Discount (10%): -1,000
- Amount Total: 9,000

**Invoice:**
```
Tuition Fee         8,000
Books Fee           2,000
Discount (10%)     -1,000
------------------------
Total               9,000 ✓
```

### Scenario 2: Scholarship Only

**Student Fee:**
- Base Amount: 10,000
- Scholarship (Merit 20%): -2,000
- Amount Total: 8,000

**Invoice:**
```
Tuition Fee                 8,000
Books Fee                   2,000
Scholarship: Merit 2024    -2,000
------------------------
Total                       8,000 ✓
```

### Scenario 3: Both Discounts

**Student Fee:**
- Base Amount: 10,000
- Discount (10%): -1,000
- Scholarship (Merit 20%): -2,000
- Amount Total: 7,000

**Invoice:**
```
Tuition Fee                 8,000
Books Fee                   2,000
Discount (10%)             -1,000
Scholarship: Merit 2024    -2,000
------------------------
Total                       7,000 ✓
```

### Scenario 4: With Late Fee

**Student Fee:**
- Base Amount: 10,000
- Discount (10%): -1,000
- Amount Total: 9,000
- Late Fee (after overdue): +450

**Invoice (after late fee applied):**
```
Tuition Fee                 8,000
Books Fee                   2,000
Discount (10%)             -1,000
Late Fee (15 days)           +450
------------------------
Total                       9,450 ✓
```

## Benefits

1. ✅ **Transparency**: Invoice clearly shows all discounts applied
2. ✅ **Accuracy**: Invoice total matches student fee amount
3. ✅ **Audit Trail**: Each discount is a separate line item
4. ✅ **Reporting**: Easy to track total discounts given
5. ✅ **Flexibility**: Can add/remove discounts independently

## Verification

To verify the fix works:

1. **Create student fee with discount:**
   ```python
   fee = env['school.student.fee'].create({
       'student_id': student.id,
       'structure_id': structure.id,
       'discount_type': 'percent',
       'discount_value': 10.0,
   })
   ```

2. **Check amount_total:**
   ```python
   print(fee.amount_total)  # Should show discounted amount
   ```

3. **Generate invoice:**
   ```python
   fee.action_generate_invoice()
   ```

4. **Check invoice total:**
   ```python
   print(fee.invoice_id.amount_total)  # Should match fee.amount_total ✓
   ```

5. **View invoice lines:**
   ```python
   for line in fee.invoice_id.invoice_line_ids:
       print(f"{line.name}: {line.price_unit}")
   # Should show discount as negative line
   ```

## Migration Notes

**For existing invoices:**
- Already generated invoices won't be updated
- They will show the original amounts without discounts
- Options:
  1. Cancel and regenerate invoices
  2. Manually add discount lines to existing invoices
  3. Keep as-is for historical records

**For new invoices:**
- All new invoices will automatically include discount lines
- Invoice total will match student fee amount_total

## Files Modified

- `models/student_fee.py`: Updated `action_generate_invoice()` method
- `data/product_data.xml`: Added discount and scholarship products

## Upgrade Instructions

```bash
# Upgrade module
./odoo-bin -u school_fees -d your_database

# Verify discount products created
# Go to: Sales → Products → Products
# Search for: "Fee Discount" and "Scholarship Discount"

# Test with new student fee
# 1. Create fee with discount
# 2. Generate invoice
# 3. Verify invoice total matches fee amount
```

## Summary

The fix ensures that discounts and scholarships are properly reflected in the invoice by adding them as separate line items with negative amounts. This provides transparency, accuracy, and a clear audit trail of all discounts applied.

**Result:** Invoice `amount_due` now correctly matches student fee `amount_total`! ✓
