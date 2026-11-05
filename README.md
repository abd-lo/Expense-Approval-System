# Simple Expense Approval System

A full-stack, containerized Expense Approval System designed for streamlined enterprise expense tracking and review. 
The platform enables employees to record, manage, and submit expense claims, while providing managers with a dedicated queue to audit, approve, or reject claims with mandatory feedback.

---

## Architecture Overview

The system follows a decoupled, Layered:

```
┌─────────────────────────────────────────────────────────────┐
│                       Client Browser                        │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP / JSON (Port 5173)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Presentation Tier (Frontend)                │
│  - React 18 SPA (Vite)                                     │
│  - Tailwind CSS                                             │
│  - High-performance Alpine Nginx Static Reverse Proxy       │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST API Calls (Port 8000)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Tier (Backend)                 │
│  - Python 3.11 + FastAPI (ASGI Engine)                     │
│  - Pydantic v2 (Validation & Serialization)                 │
│  - OAuth2 Password Bearer Flow + Stateless JWT Auth        │
│  - Deterministic State Machine Validation Layer             │
└──────────────────────────────┬──────────────────────────────┘
                               │ SQLAlchemy 2.0 ORM (Port 5432)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   Database Tier (Persistence)               │
│  - PostgreSQL 15 Engine                                     │
│  - Persistent Docker Named Volume Storage                  │
│  - Automated Idempotent User & Data Seeding                 │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python 3.11), [Uvicorn](https://www.uvicorn.org/) (ASGI Server), [Pydantic v2](https://docs.pydantic.dev/) (Schema validation), [SQLAlchemy 2.0](https://www.sqlalchemy.org/) (ORM).
* **Database:** [PostgreSQL 15](https://www.postgresql.org/) with `psycopg2-binary` driver.
* **Security & Auth:** Stateless JSON Web Tokens (`python-jose`), Passlib with `bcrypt==4.0.1` password hashing, Role-Based Access Control (RBAC).
* **Frontend:** [React 18](https://react.dev/), [Vite](https://vitejs.dev/), [Tailwind CSS](https://tailwindcss.com/), Axios API client, React Context API.
* **Orchestration & Serving:** Multi-stage `Dockerfile` configurations, [Alpine Nginx](https://nginx.org/), `docker-compose`.

---

## Getting Started & Setup

### Prerequisites
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (macOS, Windows, or Linux) installed and running.
* Ports `5173`, `8000`, and `5432` free on your host machine.

### Quick Start (Zero-Config Docker Deployment)

1. **Clone the repository:**
   ```bash
   git clone <REPO_URL>
   cd Expense-Approval-System
   ```

2. **Launch the entire stack:**
   ```bash
   docker compose up --build
   ```
   *(To run in the background, append the `-d` flag: `docker compose up --build -d`)*

3. **Access the application:**
   * **Web Client (UI):** [http://localhost:5173](http://localhost:5173)
   * **Interactive API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
   * **Alternative API Documentation (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Pre-Seeded Demo Credentials

The database seeds automatically upon startup with sample accounts sharing a uniform password:

| Role | Email | Password | Allowed Capabilities |
| :--- | :--- | :--- | :--- |
| **Manager** | `manager4@example.com` | `Password123!` | Audit all claims, approve, reject with reason |
| **Employee** | `employee5@example.com` | `Password123!` | Create, edit drafts, submit, view own claims |
| **Employee** | `employee6@example.com` | `Password123!` | Create, edit drafts, submit, view own claims |

---
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

---
## Design Decisions

### 1. Stateless JWT Authentication over Server-Side Sessions
* **Decision:** Used stateless JWT bearer tokens containing the user's ID, role, and expiration timestamp signed via HMAC-SHA256 (`HS256`).
* **Rationale:** 
  * Eliminates database or cache hits (such as Redis) purely for identity lookup on every incoming HTTP request.
  * Ensures the backend API remains horizontally scalable and stateless.
  * Enables native cross-client compatibility (web, mobile, or third-party service integration).

### 2. Explicit Action Endpoints over Generic Status Fields (Finite State Machine)
* **Decision:** The API does not expose a generic `status` field on `PUT /expenses/{id}`. State transitions occur exclusively through dedicated action endpoints:
  * `POST /expenses/{id}/submit` (`DRAFT` $\to$ `SUBMITTED`)
  * `POST /expenses/{id}/approve` (`SUBMITTED` $\to$ `APPROVED`)
  * `POST /expenses/{id}/reject` (`SUBMITTED` $\to$ `REJECTED`)
* **Rationale:** 
  * Prevents clients from arbitrary state tampering (e.g., an employee attempting to send `{ "status": "APPROVED" }`).
  * Enforces state guard clauses: claims can only be reviewed if they are actively in `SUBMITTED` status.
  * Guarantees terminal states: records marked `APPROVED` or `REJECTED` are locked against further edits or deletions.

### 3. Role-Based Access Control (RBAC) & Ownership Validation
* **Decision:** Enforced authorization at the dependency injection level using FastAPI's `Depends(require_role(...))` and domain-level object ownership checks.
* **Rationale:** 
  * Prevents **Insecure Direct Object References (IDOR)**: an employee cannot view, edit, or submit an expense owned by another user.
  * Centralizes role verification, eliminating boilerplate checks within route handler code.


---

## If I Had More Time :

If expanded further, the following features and architectural improvements would be prioritized:

### 1. Enterprise Hierarchy & Multi-Tier Approvals
* **Company Organizational Tree:** Model complex enterprise structures including Organizations, Divisions, Departments, Teams, and Executive Leadership (e.g., Team Lead $\to$ Department Manager $\to$ Finance Director $\to$ CEO).
* **Dynamic Approval Thresholds:** Route approvals based on expense amounts (e.g., under \$500 requires Manager approval; over \$5,000 escalates to the VP or CEO).
* **Comprehensive Audit Logging:** Introduce an immutable `expense_audit_logs` table tracking every actor, timestamp, previous state, and transition metadata for financial compliance.

### 2. Hardened Authentication: Refresh Tokens & Self-Service Registration
* **Public User Registration:** Implement `POST /auth/register` with email verification workflows and domain-based auto-tenant assignment.
* **Dual-Token Rotation:** Pair short-lived JWT access tokens (15-minute lifespan stored in memory) with long-lived refresh tokens stored in secure, `HttpOnly`, `SameSite=Strict` cookies backed by database token-family revocation checks.

### 3. Reporting & Business Intelligence Dashboard
* **Data Visualization:** Integrate aggregation queries with client-side charting (e.g., Recharts) displaying burn rates, monthly department spending, and category breakdowns.
* **Export Utilities:** Support asynchronous export of expense audit trails into CSV and PDF receipt formats.

### 4. UI/UX Enhancements & Detailed Views
* **Receipt Uploads:** Support file uploads (PDF/Images) directly to S3-compatible object storage with signed download URLs.
* **Rich Expense Details:** Expand the schema to accommodate multi-currency conversion, tax breakdowns, split categories, and inline manager comments.

### 5. Administrator Role & User Lifecycle Management

* **Admin Role & Permissions:** Introduce a dedicated ADMIN persona distinct from operational managers, focused on system governance, organization settings, and user provisioning.

* **Soft Deletes (is_active = False):** Implement non-destructive user deactivation. Rather than executing hard SQL DELETE operations (which break foreign key integrity and historic expense audit trails), deactivated employees are flagged is_active=False and immediately barred from authenticating via token validation middleware.

* ***Department Reassignment:** Enable administrative tools to reassign active workflows and pending approvals when an employee or manager departs the company.