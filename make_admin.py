"""
Quick helper: promote an existing user to admin.
Run: python make_admin.py someone@example.com
"""
import sys
from app.database import SessionLocal
from app import models

if len(sys.argv) != 2:
    print("Usage: python make_admin.py <email>")
    sys.exit(1)

email = sys.argv[1]
db = SessionLocal()
user = db.query(models.User).filter(models.User.email == email).first()

if not user:
    print(f"No user found with email {email}. Register that user first via /auth/register.")
else:
    user.role = models.UserRole.admin
    db.commit()
    print(f"{email} is now an admin.")

db.close()
