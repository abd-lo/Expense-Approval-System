# AI Usage & Engineering Decisions

This document outlines how AI was utilized during the development of the **Expense Approval System**, highlighting specific instances where human engineering judgment overrode AI recommendations.

---

## 1. Engineering Directives & Overrides

AI was used as a productivity assistant for scaffolding boilerplate and syntax checks. Critical architectural interventions included:

1. **Architecture Simplification (Rejecting Over-Engineering):**
   * *AI Proposal:* Suggested an overcomplicated microservices architecture with distributed messaging.
   * *Override:* Rejected this in favor of a clean, modular monolith (FastAPI + PostgreSQL + React). This eliminated unnecessary network latency, deployment overhead, and failure points within the 24-hour delivery constraint.

2. **Timezone Standardization (UTC vs. Local Time):**
   * *AI Proposal:* Generated database models and default handlers using naive local system time / deprecated `datetime.utcnow`.
   * *Override:* Enforced timezone-aware UTC (`timezone.utc`) with `TIMESTAMPTZ` columns to guarantee consistent timestamp auditing across different deployment environments and regions.

3. **Context Drift:**
   	*Resolved variable, column, and schema naming conflicts caused by the AI losing backend context across turns.

4. **Data Retention & Deletion Strategy:**
   * *AI Proposal:* Implemented destructive hard deletions (`db.delete()`) for user entities, which breaks historical expense and audit integrity.
   * *Override:* Corrected the design toward a soft-delete pattern (`is_active` boolean flag) to preserve relational integrity. *(Note: Documented as an architectural decision; full lifecycle hooks are queued under "If I had more time").*

---

## 2. Summary of AI Role

* **Where AI Accelerated Delivery:** Rapid scaffolding of initial SQLAlchemy tables, Pydantic schemas, and Docker configuration boilerplates.
* **Where Human Judgment Was Essential:** Scoping decisions, role-based boundary enforcement, relational database integrity, and debugging cross-container networking.