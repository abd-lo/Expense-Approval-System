from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
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


# 1. CREATE DRAFT
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


# 2. LIST EXPENSES (WITH FILTERS & PAGINATION)
@router.get("/", response_model=List[ExpenseResponse])
def get_expenses(
    status_filter: Optional[ExpenseStatus] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Expense)

    # Employees view only their own records; managers view all
    if current_user.role != UserRole.MANAGER:
        query = query.filter(Expense.user_id == current_user.id)

    if status_filter:
        query = query.filter(Expense.status == status_filter)
    if category:
        query = query.filter(Expense.category.ilike(f"%{category}%"))

    return query.order_by(Expense.id.desc()).offset(skip).limit(limit).all()


# 3. GET SINGLE EXPENSE
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


# 4. UPDATE DRAFT (CAN ONLY EDIT WHILE IN DRAFT STATUS)
@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_in: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    if expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot edit expenses created by other users")

    if expense.status != ExpenseStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot edit an expense in '{expense.status.value}' status. Only DRAFT items are editable.",
        )

    # Update only provided fields
    update_data = expense_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(expense, field, value)

    log = AuditLog(
        expense_id=expense.id,
        actor_id=current_user.id,
        action="UPDATED",
        from_status=expense.status.value,
        to_status=expense.status.value,
        comment="Draft updated",
    )
    db.add(log)
    db.commit()
    db.refresh(expense)
    return expense


# 5. DELETE DRAFT (CAN ONLY DELETE WHILE IN DRAFT STATUS)
@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

    if expense.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot delete expenses created by other users")

    if expense.status != ExpenseStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete an expense in '{expense.status.value}' status. Only DRAFT items can be removed.",
        )

    # Clean up associated audit logs before deleting the expense
    db.query(AuditLog).filter(AuditLog.expense_id == expense.id).delete()
    db.delete(expense)
    db.commit()
    return None


# 6. SUBMIT DRAFT
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


# 7. REVIEW (APPROVE / REJECT)
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