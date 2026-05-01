# TimeBank: A Community Skill & Resource Exchange Database System

## 📌 Project Overview

**TimeBank** is a DBMS-focused academic project that implements a **time-credit based service exchange platform**. Members exchange skills instead of money — **1 hour of service = 1 time credit**. The database manages members, skills, service requests, transactions, a credit ledger, and feedback.

> ⚡ **This is a database-first project.** All business logic (credit transfers, validations, status updates) resides in SQL — using **stored procedures**, **triggers**, and **transactions**. Python serves only as a thin interface layer.

---

## 🎯 DBMS Concepts Demonstrated

| Concept | Where |
|---------|-------|
| **Normalization (1NF → 3NF)** | `database/normalization.md` |
| **Functional Dependencies** | `database/normalization.md` |
| **DDL (CREATE TABLE)** | `database/schema.sql` |
| **DML (INSERT, UPDATE)** | `database/seed_data.sql` |
| **Constraints (PK, FK, CHECK, UNIQUE, NOT NULL)** | `database/schema.sql`, `database/constraints.sql` |
| **JOINs (INNER, LEFT)** | `database/queries.sql` |
| **Subqueries (scalar, correlated, IN)** | `database/queries.sql` |
| **Aggregations (SUM, COUNT, AVG)** | `database/queries.sql` |
| **GROUP BY + HAVING** | `database/queries.sql` |
| **Views** | `database/queries.sql` |
| **Stored Procedures & Functions** | `database/procedures.sql` |
| **Triggers** | `database/triggers.sql` |
| **Transactions (COMMIT, ROLLBACK, SAVEPOINT)** | `database/transactions.sql` |
| **ACID Properties** | `database/transactions.sql` |

---

## 📂 Project Structure

```
timebank/
│
├── app/
│   ├── __init__.py
│   ├── db.py              # DB connection (psycopg2 pool)
│   ├── queries.py          # SQL execution layer
│   ├── services.py         # Calls procedures/triggers
│
├── database/
│   ├── schema.sql          # CREATE TABLE (DDL)
│   ├── constraints.sql     # ALTER TABLE constraints
│   ├── normalization.md    # 1NF, 2NF, 3NF explanation
│   ├── procedures.sql      # Stored procedures & functions
│   ├── triggers.sql        # Database triggers
│   ├── transactions.sql    # COMMIT, ROLLBACK, SAVEPOINT
│   ├── queries.sql         # Analytical queries & views
│   ├── seed_data.sql       # Sample data
│
├── frontend/
│   ├── __init__.py
│   ├── streamlit_app.py    # Streamlit UI
│
├── .env                    # Database credentials
├── .env.example            # Template for .env
├── .gitignore
├── ER-Diagram.png          # Entity-Relationship diagram
├── README.md               # This file
├── requirements.txt        # Python dependencies
```

---

## 🗄️ Database Schema

### Entity-Relationship Overview

| Table | Description |
|-------|-------------|
| **Member** | Registered community members |
| **Skill** | Master list of exchangeable skills |
| **Member_Skill** | Bridge table (many-to-many: Member ↔ Skill) |
| **Service_Request** | Service requests posted by members |
| **Service_Transaction** | Completed service exchanges |
| **Time_Credit_Ledger** | Immutable audit trail of credit movements |
| **Feedback** | Ratings and reviews after service completion |

### Key Relationships
- A **Member** can offer many **Skills** (via **Member_Skill**)
- A **Member** can create many **Service_Requests**
- A **Service_Transaction** links a provider, requester, skill, and request
- **Time_Credit_Ledger** records every credit movement (CREDIT/DEBIT/BONUS)
- **Feedback** is tied to a completed transaction

---

## 🔧 Setup Instructions

### Prerequisites
- **PostgreSQL** 12+ installed and running
- **Python** 3.8+
- **pip** package manager

### Step 1: Clone and Navigate
```bash
cd timebank
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create the Database
```sql
-- In PostgreSQL (psql or pgAdmin):
CREATE DATABASE timebank;
```

### Step 5: Configure Environment
```bash
# Copy .env.example to .env and update with your credentials:
cp .env.example .env
# Edit .env with your PostgreSQL password
```

### Step 6: Initialize Database
Run the SQL files in this order:
```bash
psql -U postgres -d timebank -f database/schema.sql
psql -U postgres -d timebank -f database/constraints.sql
psql -U postgres -d timebank -f database/procedures.sql
psql -U postgres -d timebank -f database/triggers.sql
psql -U postgres -d timebank -f database/queries.sql     # Creates views
psql -U postgres -d timebank -f database/seed_data.sql
```

Or in **pgAdmin**: Open each file and execute in the above order.

### Step 7: Run the Application
```bash
streamlit run frontend/streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 💡 How the Credit System Works

1. **New members** receive **5 starter credits** (via `sp_register_member` procedure)
2. **Requesting a service** requires sufficient credits (checked via procedure)
3. **When a transaction completes**:
   - Provider receives credits (trigger: `trg_after_transaction_complete`)
   - Requester's credits are deducted (same trigger)
   - Both entries are logged in `Time_Credit_Ledger` (trigger)
4. **All credit logic is in SQL** — Python never manipulates balances directly

---

## 📊 Streamlit UI Pages

| Page | Description |
|------|-------------|
| 🏠 Home | Overview with member/skill/transaction counts |
| 👤 Register Member | Form to add new members (calls procedure) |
| 🛠️ Add Skill | Assign skills to member profiles |
| 📋 Request Service | Create service requests |
| ✅ Complete Transaction | Match provider to request and complete exchange |
| 💰 View Credits | Credit balances, ledger history |
| ⭐ Give Feedback | Rate and review completed transactions |
| 📊 Analytics | Charts and tables for top members, popular skills |

---

## 📝 Normalization

The database is normalized to **Third Normal Form (3NF)**:

- **1NF**: All values atomic, no repeating groups, unique rows via primary keys
- **2NF**: No partial dependencies (all non-key attributes depend on full PKs)
- **3NF**: No transitive dependencies (all attributes depend directly on PKs)

See [`database/normalization.md`](database/normalization.md) for detailed explanation with examples.

---

## ⚠️ Design Principles

- ✅ **Database-first**: All business logic in SQL (procedures, triggers, transactions)
- ✅ **No ORM**: Direct SQL queries via `psycopg2`
- ✅ **Thin Python layer**: Python only executes SQL and renders UI
- ✅ **ACID compliance**: Demonstrated through transaction examples
- ✅ **Referential integrity**: Foreign keys, cascading deletes, check constraints

---

## 📄 License

Academic project — for educational purposes only.
