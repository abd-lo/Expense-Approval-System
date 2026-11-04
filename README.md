# Expense-Approval-System

## Initial Overview & Architecture

An Expense Approval System is an internal company platform designed to digitize employee reimbursement requests, replacing ad-hoc emails and paper receipts with an auditable approval workflow.

### User Roles
- **Employee (Submitter):** Creates expense entries (amount, category, description), saves them as drafts, submits them for review, and tracks their status.
- **Manager (Approver):** Views a queue of submitted expenses across the organization and decides whether to approve or reject them (with mandatory feedback on rejection).

### Expense Lifecycle (State Machine)
Expenses progress through four explicit states:
1. **DRAFT:** The expense is editable only by the author and invisible to approvers.
2. **SUBMITTED:** The expense is locked against regular edits and appears in the manager's review queue.
3. **APPROVED:** The manager accepts the expense; it is permanently locked and flagged for disbursement.
4. **REJECTED:** The manager rejects the expense with a recorded explanation.

### Core Business Rules
- **No Self-Approval:** A user can never approve or reject an expense they submitted, even if they possess manager credentials.
- **State Immutability:** Once an expense transitions past `DRAFT`, its financial details (amount, category, currency) cannot be modified or deleted.
- **Immutable Audit Trail:** Every status transition automatically appends a record tracking the actor ID, previous state, new state, timestamp, and optional comment.

### Tech Stack
- **Frontend:** React (SPA for authentication, expense authoring, and review queues)
- **Backend:** FastAPI (Python REST API handling authentication, role-based access control, and state machine transitions)
- **Database:** PostgreSQL (Relational persistence with foreign keys and relational constraints)
- **Containerization:** Docker Compose (Single-command deployment for DB, API, and Web UI)
