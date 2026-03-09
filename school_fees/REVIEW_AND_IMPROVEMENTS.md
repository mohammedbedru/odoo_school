# School Fees Module - Review and Improvements

## Current Approach Review

### ✅ What's Good

1. **Clean Separation of Concerns**
   - Fee Structure (template/pricing)
   - Student Fee (individual fee records)
   - Bulk Invoice Wizard (mass operations)

2. **Integration with Odoo Accounting**
   - Uses `account.move` for invoices
   - Proper invoice line creation
   - Payment state tracking

3. **Data Integrity**
   - SQL constraint prevents duplicate fees per student/term
   - Validation for missing partner
   - Validation for duplicate invoices

4. **Chatter Integration**
   - Both models inherit mail.thread
   - Good for audit trail

5. **Multi-currency Support**
   - Currency field properly defined
   - Related to company currency

### ⚠️ Issues and Improvements Needed

## Critical Issues

### 1. **Payment State Not Auto-Updating**

**Problem:**
```python
payment_state = fields.Selection(
    related="invoice_id.payment_state",
    store=True,
    readonly=True
)
```
This is a related field but won't auto-update when invoice payment changes.

**Solution:** Use computed field with proper dependency or scheduled action.

### 2. **State Management Incomplete**

**Problem:**
- State changes from `draft` → `invoiced` automatically
- But `invoiced` → `paid` requires manual button click
- No handling for cancelled/refunded invoices

**Solution:** Implement proper state transitions with invoice hooks.

### 3. **No Discount/Scholarship Support**

**Problem:** No way to apply discounts or scholarships to students.

**Solution:** Add discount fields and scholarship management.

### 4. **No Partial Payment Tracking**

**Problem:** Only tracks fully paid vs unpaid.

**Solution:** Add fields for amount paid, amount due, payment history.

### 5. **Missing Fee Categories**

**Problem:** All fees are flat products, no categorization.

**Solution:** Add fee categories (Tuition, Transport, Books, etc.).

### 6. **No Late Fee Calculation**

**Problem:** No automatic late fees for overdue payments.

**Solution:** Add due date and late fee configuration.

### 7. **Limited Reporting**

**Problem:** No built-in reports for:
- Outstanding fees
- Payment collection summary
- Fee defaulters list

**Solution:** Add comprehensive reports.

### 8. **No Sibling Discount**

**Problem:** Common requirement in schools not supported.

**Solution:** Add sibling discount configuration.

## Recommended Improvements

### Priority 1: Critical Fixes

#### 1.1 Fix Payment State Tracking

```python
# In student_fee.py
payment_state = fields.Selection([
    ('not_paid', 'Not Paid'),
    ('in_payment', 'In Payment'),
    ('paid', 'Paid'),
    ('partial', 'Partially Paid'),
    ('reversed', 'Reversed'),
    ('invoicing_legacy', 'Invoicing App Legacy'),
], string='Payment Status', compute='_compute_payment_state', store=True)

amount_paid = fields.Monetary(
    compute='_compute_payment_amounts',
    store=True,
    currency_field='currency_id'
)

amount_due = fields.Monetary(
    compute='_compute_payment_amounts',
    store=True,
    currency_field='currency_id'
)

@api.depends('invoice_id.payment_state', 'invoice_id.amount_residual')
def _compute_payment_state(self):
    for rec in self:
        if rec.invoice_id:
            rec.payment_state = rec.invoice_id.payment_state
            # Auto-update state based on payment
            if rec.invoice_id.payment_state == 'paid' and rec.state == 'invoiced':
                rec.state = 'paid'
        else:
            rec.payment_state = 'not_paid'

@api.depends('invoice_id.amount_total', 'invoice_id.amount_residual')
def _compute_payment_amounts(self):
    for rec in self:
        if rec.invoice_id:
            rec.amount_paid = rec.invoice_id.amount_total - rec.invoice_id.amount_residual
            rec.amount_due = rec.invoice_id.amount_residual
        else:
            rec.amount_paid = 0.0
            rec.amount_due = rec.amount_total
```

#### 1.2 Add Discount Support

```python
# In student_fee.py
discount_type = fields.Selection([
    ('percent', 'Percentage'),
    ('fixed', 'Fixed Amount'),
], string='Discount Type')

discount_value = fields.Float(string='Discount Value')

discount_amount = fields.Monetary(
    compute='_compute_discount',
    store=True,
    currency_field='currency_id'
)

scholarship_id = fields.Many2one('school.scholarship', string='Scholarship')

@api.depends('structure_id.total_amount', 'discount_type', 'discount_value', 'scholarship_id')
def _compute_amount_total(self):
    for rec in self:
        base_amount = rec.structure_id.total_amount
        discount = 0.0
        
        # Apply discount
        if rec.discount_type == 'percent':
            discount = base_amount * (rec.discount_value / 100)
        elif rec.discount_type == 'fixed':
            discount = rec.discount_value
        
        # Apply scholarship
        if rec.scholarship_id:
            discount += rec.scholarship_id.amount
        
        rec.discount_amount = discount
        rec.amount_total = base_amount - discount
```

#### 1.3 Add Due Date and Late Fees

```python
# In student_fee.py
due_date = fields.Date(string='Due Date', required=True, tracking=True)

is_overdue = fields.Boolean(
    compute='_compute_overdue',
    store=True,
    string='Overdue'
)

days_overdue = fields.Integer(
    compute='_compute_overdue',
    store=True
)

late_fee_amount = fields.Monetary(
    compute='_compute_late_fee',
    store=True,
    currency_field='currency_id'
)

@api.depends('due_date', 'payment_state')
def _compute_overdue(self):
    today = fields.Date.today()
    for rec in self:
        if rec.payment_state != 'paid' and rec.due_date:
            if rec.due_date < today:
                rec.is_overdue = True
                rec.days_overdue = (today - rec.due_date).days
            else:
                rec.is_overdue = False
                rec.days_overdue = 0
        else:
            rec.is_overdue = False
            rec.days_overdue = 0

@api.depends('days_overdue', 'amount_total')
def _compute_late_fee(self):
    for rec in self:
        if rec.is_overdue and rec.days_overdue > 0:
            # Example: 1% per week overdue, max 10%
            weeks_overdue = rec.days_overdue // 7
            late_fee_percent = min(weeks_overdue * 1, 10)
            rec.late_fee_amount = rec.amount_total * (late_fee_percent / 100)
        else:
            rec.late_fee_amount = 0.0
```

### Priority 2: Enhanced Features

#### 2.1 Add Fee Categories

```python
# New model: fee_category.py
class SchoolFeeCategory(models.Model):
    _name = "school.fee.category"
    _description = "Fee Category"
    
    name = fields.Char(required=True)
    code = fields.Char(required=True)
    description = fields.Text()
    is_mandatory = fields.Boolean(default=True)
    
    _sql_constraints = [
        ('code_unique', 'unique(code)', 'Category code must be unique!')
    ]

# Update fee_structure.py
class SchoolFeeStructureLine(models.Model):
    _name = "school.fee.structure.line"
    _description = "Fee Structure Line"

    structure_id = fields.Many2one("school.fee.structure", required=True, ondelete="cascade")
    category_id = fields.Many2one("school.fee.category", required=True)
    product_id = fields.Many2one("product.product", required=True)
    amount = fields.Monetary(required=True)
    is_optional = fields.Boolean(default=False)
    currency_id = fields.Many2one(
        related="structure_id.currency_id",
        store=True,
        readonly=True
    )
```

#### 2.2 Add Sibling Discount

```python
# In student_fee.py
has_sibling_discount = fields.Boolean(
    compute='_compute_sibling_discount',
    store=True
)

sibling_discount_amount = fields.Monetary(
    compute='_compute_sibling_discount',
    store=True,
    currency_field='currency_id'
)

@api.depends('student_id')
def _compute_sibling_discount(self):
    for rec in self:
        # Find siblings in same school
        siblings = self.env['school.student'].search([
            ('id', '!=', rec.student_id.id),
            ('parent_id', '=', rec.student_id.parent_id.id),
            ('status', 'in', ['enrolled', 'active'])
        ])
        
        if len(siblings) > 0:
            rec.has_sibling_discount = True
            # Example: 10% discount for 2nd child, 15% for 3rd+
            if len(siblings) == 1:
                discount_percent = 10
            else:
                discount_percent = 15
            rec.sibling_discount_amount = rec.amount_total * (discount_percent / 100)
        else:
            rec.has_sibling_discount = False
            rec.sibling_discount_amount = 0.0
```

#### 2.3 Add Payment Plan Support

```python
# New model: payment_plan.py
class SchoolFeePaymentPlan(models.Model):
    _name = "school.fee.payment.plan"
    _description = "Fee Payment Plan"
    
    student_fee_id = fields.Many2one('school.student.fee', required=True, ondelete='cascade')
    installment_number = fields.Integer(required=True)
    due_date = fields.Date(required=True)
    amount = fields.Monetary(required=True)
    currency_id = fields.Many2one(related='student_fee_id.currency_id')
    is_paid = fields.Boolean(default=False)
    payment_date = fields.Date()
    invoice_id = fields.Many2one('account.move')
```

### Priority 3: Reporting and Analytics

#### 3.1 Add Dashboard/Reports

```python
# Add to student_fee.py
def action_open_fee_dashboard(self):
    return {
        'type': 'ir.actions.act_window',
        'name': 'Fee Dashboard',
        'res_model': 'school.student.fee',
        'view_mode': 'graph,pivot',
        'context': {
            'search_default_current_year': 1,
        }
    }
```

#### 3.2 Add Outstanding Fees Report

Create a new report model:

```python
# models/fee_report.py
class SchoolFeeReport(models.Model):
    _name = "school.fee.report"
    _description = "Fee Analysis Report"
    _auto = False
    _rec_name = 'student_id'

    student_id = fields.Many2one('school.student', readonly=True)
    grade_id = fields.Many2one('school.grade', readonly=True)
    academic_year_id = fields.Many2one('school.academic.year', readonly=True)
    term = fields.Selection([
        ("t1", "Term 1"),
        ("t2", "Term 2"),
        ("t3", "Term 3"),
    ], readonly=True)
    amount_total = fields.Monetary(readonly=True)
    amount_paid = fields.Monetary(readonly=True)
    amount_due = fields.Monetary(readonly=True)
    payment_state = fields.Selection([
        ('not_paid', 'Not Paid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
    ], readonly=True)
    is_overdue = fields.Boolean(readonly=True)
    days_overdue = fields.Integer(readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT
                    sf.id,
                    sf.student_id,
                    s.grade_id,
                    sf.academic_year_id,
                    sf.term,
                    sf.amount_total,
                    COALESCE(am.amount_total - am.amount_residual, 0) as amount_paid,
                    COALESCE(am.amount_residual, sf.amount_total) as amount_due,
                    CASE
                        WHEN am.payment_state = 'paid' THEN 'paid'
                        WHEN am.amount_residual < am.amount_total THEN 'partial'
                        ELSE 'not_paid'
                    END as payment_state,
                    CASE WHEN sf.due_date < CURRENT_DATE AND am.payment_state != 'paid' THEN TRUE ELSE FALSE END as is_overdue,
                    CASE WHEN sf.due_date < CURRENT_DATE THEN CURRENT_DATE - sf.due_date ELSE 0 END as days_overdue
                FROM school_student_fee sf
                LEFT JOIN school_student s ON s.id = sf.student_id
                LEFT JOIN account_move am ON am.id = sf.invoice_id
            )
        """ % self._table)
```

### Priority 4: User Experience

#### 4.1 Add Smart Buttons

```python
# In student_fee.py
invoice_count = fields.Integer(compute='_compute_invoice_count')
payment_count = fields.Integer(compute='_compute_payment_count')

def _compute_invoice_count(self):
    for rec in self:
        rec.invoice_count = 1 if rec.invoice_id else 0

def _compute_payment_count(self):
    for rec in self:
        if rec.invoice_id:
            rec.payment_count = len(rec.invoice_id.payment_ids)
        else:
            rec.payment_count = 0

def action_view_payments(self):
    self.ensure_one()
    return {
        'type': 'ir.actions.act_window',
        'name': 'Payments',
        'res_model': 'account.payment',
        'view_mode': 'list,form',
        'domain': [('id', 'in', self.invoice_id.payment_ids.ids)],
    }
```

#### 4.2 Add Filters and Groups

Update views with better filters:

```xml
<search>
    <field name="student_id"/>
    <field name="academic_year_id"/>
    <separator/>
    <filter string="Unpaid" name="unpaid" domain="[('payment_state', '!=', 'paid')]"/>
    <filter string="Overdue" name="overdue" domain="[('is_overdue', '=', True)]"/>
    <filter string="Paid" name="paid" domain="[('payment_state', '=', 'paid')]"/>
    <separator/>
    <filter string="Current Year" name="current_year" 
            domain="[('academic_year_id.is_current', '=', True)]"/>
    <group expand="0" string="Group By">
        <filter string="Student" name="group_student" context="{'group_by': 'student_id'}"/>
        <filter string="Grade" name="group_grade" context="{'group_by': 'student_id.grade_id'}"/>
        <filter string="Term" name="group_term" context="{'group_by': 'term'}"/>
        <filter string="Payment Status" name="group_payment" context="{'group_by': 'payment_state'}"/>
    </group>
</search>
```

### Priority 5: Security and Access Rights

#### 5.1 Add Record Rules

```xml
<!-- security/security_rules.xml -->
<record id="student_fee_rule_own_student" model="ir.rule">
    <field name="name">Student: Own Fees Only</field>
    <field name="model_id" ref="model_school_student_fee"/>
    <field name="domain_force">[('student_id.user_id', '=', user.id)]</field>
    <field name="groups" eval="[(4, ref('school_core.group_school_student'))]"/>
</record>

<record id="student_fee_rule_accountant" model="ir.rule">
    <field name="name">Accountant: All Fees</field>
    <field name="model_id" ref="model_school_student_fee"/>
    <field name="domain_force">[(1, '=', 1)]</field>
    <field name="groups" eval="[(4, ref('group_school_fees_accountant'))]"/>
</record>
```

## Implementation Priority

### Phase 1 (Critical - Week 1)
1. Fix payment state tracking
2. Add amount_paid and amount_due fields
3. Add due_date field
4. Fix state transitions

### Phase 2 (Important - Week 2)
1. Add discount support
2. Add late fee calculation
3. Add fee categories
4. Improve views with smart buttons

### Phase 3 (Enhanced - Week 3)
1. Add sibling discount
2. Add payment plan support
3. Add scholarship management
4. Add comprehensive reports

### Phase 4 (Polish - Week 4)
1. Add dashboard
2. Add email notifications
3. Add payment reminders
4. Add parent portal access

## Testing Checklist

- [ ] Create fee structure for a grade
- [ ] Generate invoice for single student
- [ ] Generate bulk invoices for section
- [ ] Register payment and verify state updates
- [ ] Apply discount and verify calculation
- [ ] Test overdue fee calculation
- [ ] Test sibling discount
- [ ] Generate fee statement report
- [ ] Test access rights for different user roles
- [ ] Test with multiple currencies

## Conclusion

The current approach is **solid and well-structured**, but needs enhancements for production use. The main improvements needed are:

1. **Automated payment tracking** (Critical)
2. **Discount/scholarship support** (Important)
3. **Better reporting** (Important)
4. **Enhanced user experience** (Nice to have)

The foundation is good - just needs these additions to be production-ready!
