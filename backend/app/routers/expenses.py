from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user, require_manager
from app.models import Expense, AuditLog, User, UserRole, ExpenseStatus
from app.schemas import (
    ExpenseCreate,
    ExpenseUpdate,
    ExpenseResponse,
    ExpenseReview,
)

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_in: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = Expense(
        **expense_in.model_dump(),
        user_id=current_user.id,
        status=ExpenseStatus.DRAFT,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    # Initial audit log entry
    log = AuditLog(
        expense_id=expense.id,
        actor_id=current_user.id,
        action="CREATED",
        from_status=None,
        to_status=ExpenseStatus.DRAFT.value,
        comment="Draft created",
    )
    db.add(log)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Managers see all expenses; regular employees see only their own
    if current_user.role == UserRole.MANAGER:
        return db.query(Expense).all()
    return db.query(Expense).filter(Expense.user_id == current_user.id).all()


@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense_by_id(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    if current_user.role != UserRole.MANAGER and expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

    return expense


@router.post("/{expense_id}/submit", response_model=ExpenseResponse)
def submit_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    if expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only submit your own expenses")

    if expense.status != ExpenseStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit an expense with status '{expense.status.value}'",
        )

    old_status = expense.status.value
    expense.status = ExpenseStatus.SUBMITTED

    log = AuditLog(
        expense_id=expense.id,
        actor_id=current_user.id,
        action="SUBMITTED",
        from_status=old_status,
        to_status=ExpenseStatus.SUBMITTED.value,
        comment="Submitted for approval",
    )
    db.add(log)
    db.commit()
    db.refresh(expense)
    return expense


@router.post("/{expense_id}/review", response_model=ExpenseResponse)
def review_expense(
    expense_id: int,
    review_in: ExpenseReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    # Anti-Self-Approval check (ABAC)
    if expense.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Separation of duties violation: You cannot approve or reject your own expense",
        )

    # State machine check
    if expense.status != ExpenseStatus.SUBMITTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Expense must be in SUBMITTED state to be reviewed (current: '{expense.status.value}')",
        )

    old_status = expense.status.value

    if review_in.action == "APPROVE":
        expense.status = ExpenseStatus.APPROVED
        expense.rejection_reason = None
    elif review_in.action == "REJECT":
        if not review_in.rejection_reason:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A rejection reason is required when rejecting an expense",
            )
        expense.status = ExpenseStatus.REJECTED
        expense.rejection_reason = review_in.rejection_reason

    # Add audit log entry
    log = AuditLog(
        expense_id=expense.id,
        actor_id=current_user.id,
        action=review_in.action,
        from_status=old_status,
        to_status=expense.status.value,
        comment=review_in.comment or review_in.rejection_reason,
    )
    db.add(log)
    db.commit()
    db.refresh(expense)
    return expense