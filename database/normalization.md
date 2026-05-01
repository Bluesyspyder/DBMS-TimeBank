# TimeBank Database Normalization

## Overview

The TimeBank database schema has been designed following normalization principles up to **Third Normal Form (3NF)**. This document explains the normalization process, functional dependencies, and design rationale.

---

## Functional Dependencies

### Member Table
```
member_id → first_name, last_name, email, phone, date_of_birth, address, city, state, zip_code, is_verified, credit_balance, joined_date, updated_at
email → member_id  (candidate key)
```

### Skill Table
```
skill_id → skill_name, category, description, created_at
skill_name → skill_id  (candidate key)
```

### Member_Skill Table
```
member_skill_id → member_id, skill_id, proficiency, hourly_rate, is_active, added_date
(member_id, skill_id) → proficiency, hourly_rate, is_active, added_date  (candidate key)
```

### Service_Request Table
```
request_id → requester_id, skill_id, title, description, estimated_hours, status, urgency, created_at, updated_at
```

### Service_Transaction Table
```
transaction_id → request_id, provider_id, requester_id, skill_id, hours_spent, credits_exchanged, status, started_at, completed_at, notes
```

### Time_Credit_Ledger Table
```
ledger_id → member_id, transaction_id, credit_type, amount, balance_after, description, created_at
```

### Feedback Table
```
feedback_id → transaction_id, reviewer_id, reviewee_id, rating, comment, created_at
(transaction_id, reviewer_id) → reviewee_id, rating, comment  (candidate key)
```

---

## First Normal Form (1NF)

**Rule**: All attributes must contain atomic (indivisible) values, every record must be unique, and each column must contain values of a single type.

### How TimeBank satisfies 1NF:

1. **Atomic Values**: All columns store single, indivisible values.
   - Member name is split into `first_name` and `last_name` (not a single "full_name").
   - Address components are separated into `address`, `city`, `state`, `zip_code`.
   - No multi-valued attributes (e.g., a member's skills are in a separate `Member_Skill` table, not a comma-separated list).

2. **Unique Records**: Every table has a primary key (`SERIAL`) ensuring row uniqueness.

3. **Single-type Columns**: Each column has a defined data type (VARCHAR, INT, DECIMAL, etc.).

### Example of 1NF violation (avoided):

❌ **Bad Design (violates 1NF)**:
```
Member(member_id, name, skills)
1, "John Doe", "Cooking, Tutoring, Plumbing"
```

✅ **Our Design (satisfies 1NF)**:
```
Member(member_id, first_name, last_name, ...)
Member_Skill(member_skill_id, member_id, skill_id, ...)
```

---

## Second Normal Form (2NF)

**Rule**: Must be in 1NF, and every non-key attribute must be fully functionally dependent on the entire primary key (no partial dependencies).

### How TimeBank satisfies 2NF:

1. **Single-column Primary Keys**: Tables like `Member`, `Skill`, `Service_Request`, `Service_Transaction`, `Time_Credit_Ledger`, and `Feedback` all use single-column surrogate primary keys (`SERIAL`). Partial dependency is impossible with single-column keys.

2. **Composite Key Handling**: The `Member_Skill` bridge table has a composite candidate key `(member_id, skill_id)`. All non-key attributes (`proficiency`, `hourly_rate`, `is_active`) depend on the **full combination** of member and skill, not on either individually.

### Example of 2NF violation (avoided):

❌ **Bad Design (violates 2NF)**:
```
Member_Skill(member_id, skill_id, proficiency, member_name, skill_name)
-- member_name depends only on member_id (partial dependency)
-- skill_name depends only on skill_id (partial dependency)
```

✅ **Our Design (satisfies 2NF)**:
```
Member_Skill(member_skill_id, member_id, skill_id, proficiency, hourly_rate, is_active)
-- All non-key attributes depend on the full (member_id, skill_id) combination
-- member_name is in Member table, skill_name is in Skill table
```

---

## Third Normal Form (3NF)

**Rule**: Must be in 2NF, and no non-key attribute can transitively depend on the primary key (no transitive dependencies).

### How TimeBank satisfies 3NF:

1. **No Transitive Dependencies**: In the `Member` table, all attributes (`first_name`, `email`, `phone`, etc.) depend directly on `member_id`. There is no attribute that depends on another non-key attribute.

2. **Separate Entity Tables**: Skills are in their own table rather than embedded in `Member_Skill`. Transaction details are separate from request details. Feedback is separate from transactions.

3. **Ledger Independence**: The `Time_Credit_Ledger` records each credit movement independently with `balance_after`, rather than deriving it from summing previous entries (denormalization for audit purposes, which is acceptable).

### Example of 3NF violation (avoided):

❌ **Bad Design (violates 3NF)**:
```
Service_Transaction(transaction_id, provider_id, provider_name, provider_email, ...)
-- provider_name depends on provider_id, not transaction_id (transitive dependency)
-- provider_id → provider_name (through Member table)
```

✅ **Our Design (satisfies 3NF)**:
```
Service_Transaction(transaction_id, provider_id, requester_id, ...)
Member(member_id, first_name, last_name, email, ...)
-- Provider/requester details accessed via JOIN, no transitive dependency
```

---

## Entity-Relationship Summary

| Table | Type | Key Relationships |
|-------|------|-------------------|
| Member | Entity | Independent |
| Skill | Entity | Independent |
| Member_Skill | Bridge (M:N) | Member ↔ Skill |
| Service_Request | Entity | Member → Request, Skill → Request |
| Service_Transaction | Entity | Request → Transaction, Member → Transaction |
| Time_Credit_Ledger | Audit Log | Member → Ledger, Transaction → Ledger |
| Feedback | Entity | Transaction → Feedback, Member → Feedback |

---

## Conclusion

The TimeBank schema is fully normalized to **3NF**:
- **1NF**: All values are atomic; no repeating groups; unique rows via primary keys.
- **2NF**: No partial dependencies; all non-key attributes fully depend on complete primary keys.
- **3NF**: No transitive dependencies; all non-key attributes depend directly on primary keys.

This design minimizes data redundancy, ensures data integrity, and supports efficient querying through well-defined relationships and indexes.
