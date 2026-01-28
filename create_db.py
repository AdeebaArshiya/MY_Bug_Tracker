from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # 1. Create the Database Tables
        db.create_all()
        print("Database tables created.")

        # 2. Check if Admin already exists
        if not User.query.filter_by(email="admin@test.com").first():
            # 3. Create the Admin User
            admin = User(
                username="Admin",
                email="admin@test.com",
                password=generate_password_hash("admin123"), # Hashing the password
                role="admin"
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin created successfully!")
            print("Login Email: admin@test.com")
            print("Login Password: admin123")
        else:
            print("⚠️ Admin already exists.")

if __name__ == "__main__":
    create_admin()