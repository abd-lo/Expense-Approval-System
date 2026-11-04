from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User, UserRole
from app.security import get_password_hash

def seed_initial_data():
    db: Session = SessionLocal()
    try:
        users = [
            {
                "email": "manager4@example.com",
                "full_name": "Manager User",
                "role": UserRole.MANAGER,
                "password": "Password123!",
            },
            {
                "email": "employee5@example.com",
                "full_name": "Employee One",
                "role": UserRole.EMPLOYEE,
                "password": "Password123!",
            },
            {
                "email": "employee6@example.com",
                "full_name": "Employee Two",
                "role": UserRole.EMPLOYEE,
                "password": "Password123!",
            },
        ]

        for user_data in users:
            existing = db.query(User).filter(User.email == user_data["email"]).first()
            if not existing:
                user = User(
                    email=user_data["email"],
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    hashed_password=get_password_hash(user_data["password"]),
                )
                db.add(user)
                print(f"[Seed] Created demo user: {user_data['email']} ({user_data['role'].value})")

        db.commit()
    except Exception as e:
        print(f"[Seed] Error seeding users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_initial_data()