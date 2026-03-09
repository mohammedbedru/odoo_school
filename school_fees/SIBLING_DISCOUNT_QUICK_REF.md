# Sibling Discount - Quick Reference Card

## 🎯 What It Does
Automatically applies discounts to students with siblings enrolled in the same academic year.

## 📊 Discount Rates (Default)
| Siblings | Discount |
|----------|----------|
| 2        | 10%      |
| 3        | 15%      |
| 4+       | 20%      |

## 🔧 How to Use

### Automatic (Default)
1. Ensure students have guardians set (`parent_ids`)
2. Create student fee
3. Discount applies automatically ✅

### Manual Control
```
Student Fee Form → Sibling Discount Section
☑ Apply Sibling Discount (uncheck to disable)
```

## 📋 What You'll See

### Form View
```
Sibling Discount Section:
├─ Apply Sibling Discount: ☑
├─ Has Sibling Discount: Yes
├─ Number of Siblings: 2
├─ Sibling Discount %: 15.0
└─ Sibling Discount: $1,500.00
```

### Invoice
```
Invoice Lines:
├─ Tuition Fee: $10,000.00
├─ Books Fee: $500.00
└─ Sibling Discount (3 siblings - 15%): -$1,575.00
    Total: $8,925.00
```

## ⚙️ Configuration

### Change Discount Rates
```
Settings → Technical → System Parameters

school_fees.sibling_discount_2 = 10.0
school_fees.sibling_discount_3 = 15.0
school_fees.sibling_discount_4_plus = 20.0
```

## 🔍 Requirements for Sibling Detection
- ✅ Share at least one parent/guardian
- ✅ Same academic year
- ✅ Status: Enrolled or Active
- ✅ "Apply Sibling Discount" enabled

## 💡 Examples

### Example 1: Two Siblings
```
Parent: John Smith
Students: Alice (Grade 5), Bob (Grade 3)

Alice Fee: $10,000 → $9,000 (10% off)
Bob Fee: $8,000 → $7,200 (10% off)
Family Saves: $1,800
```

### Example 2: Three Siblings
```
Parent: Jane Doe
Students: Charlie, Diana, Emma

Each gets 15% discount
Total family savings increases!
```

## 🚫 When Discount Doesn't Apply
- Different academic years
- Inactive/dropped students
- No shared parents
- "Apply Sibling Discount" unchecked

## 🔗 Combined Discounts
```
Base Fee: $10,000
Manual Discount (5%): -$500
Scholarship (10%): -$1,000
Sibling Discount (15%): -$1,500
Final: $7,000 ✅
```

## 📱 Quick Actions

### View Sibling Discounts
```
School Fees → Student Fees
Filter: "With Sibling Discount"
```

### Disable for One Student
```
Open Fee → Uncheck "Apply Sibling Discount" → Save
```

### Check Discount Details
```
Open Fee → Sibling Discount Section
View: Count, Percentage, Amount
```

## 🐛 Troubleshooting

### Siblings Not Detected?
1. Check parent_ids are set
2. Verify same academic year
3. Confirm status is active/enrolled

### Wrong Discount?
1. Check sibling count
2. Verify system parameters
3. Ensure fee is in draft state

### Not on Invoice?
1. Verify product exists: `product_sibling_discount`
2. Check discount amount > 0
3. Regenerate invoice if needed

## 📚 Documentation
- Full Details: `SIBLING_DISCOUNT_IMPLEMENTATION.md`
- Testing: `SIBLING_DISCOUNT_TEST_GUIDE.md`
- Summary: `SIBLING_DISCOUNT_SUMMARY.md`

## ✅ Status
**PRODUCTION READY** - Fully implemented and tested

---

**Need Help?** Check the full documentation files or contact support.
