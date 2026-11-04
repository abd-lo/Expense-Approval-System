from decimal import Decimal
from datetime import datetime
from typing import Optional,List
from pydantic import BaseModel, EmailStr,Field
from app.models import ExpenseStatus,UserRole

# Base user fields
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.EMPLOYEE

# DTO used for incoming registration payload
class UserCreate(UserBase):
    password: str

# DTO returned to client (excludes password hash)
class UserResponse(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True

# Token response DTO
class Token(BaseModel):
    access_token: str
    token_type: str

# Payload decoded from JWT
class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

# ==========================================
# EXPENSE & AUDIT LOG SCHEMAS
# ==========================================

# Base fields shared by input and output
class ExpenseBase(BaseModel):
    title: str = Field(..., max_length=150)
    description: Optional[str] = None
    amount: Decimal = Field(..., gt=0, decimal_places=2)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    category: str = Field(..., max_length=50)


# Payload sent when an employee creates an expense
class ExpenseCreate(ExpenseBase):
    pass


# Payload sent when updating an existing draft expense
class ExpenseUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=150)
    description: Optional[str] = None
    amount: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    category: Optional[str] = Field(None, max_length=50)


# Payload sent by manager to approve or reject an expense
class ExpenseReview(BaseModel):
    action: str = Field(..., pattern="^(APPROVE|REJECT)$")
    rejection_reason: Optional[str] = None
    comment: Optional[str] = None


# Audit log response DTO (matches audit_logs table)
class AuditLogResponse(BaseModel):
    id: int
    actor_id: int
    action: str
    from_status: Optional[str] = None
    to_status: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Expense returned to client (matches PostgreSQL expenses table + audit history)
class ExpenseResponse(ExpenseBase):
    id: int
    status: ExpenseStatus
    rejection_reason: Optional[str] = None
    user_id: int
    created_at: datetime
    updated_at: datetime
    audit_logs: List[AuditLogResponse] = []

    class Config:
        from_attributes = True