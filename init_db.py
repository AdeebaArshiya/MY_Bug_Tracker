from app import app, db, User, Project

def setup_database():
    with app.app_context():
        print("Creating database tables...")
        # This generates the bugtracker.db file
        db.create_all()
        
        # Check if we need to add seed data
        if not User.query.filter_by(username='admin').first():
            print("Adding default admin user...")
            admin = User(username='admin', password='password123', role='admin')
            db.session.add(admin)
            
        if not Project.query.first():
            print("Adding default project...")
            project = Project(name="Default Project")
            db.session.add(project)
            
        db.session.commit()
        print("Database initialized successfully!")

if __name__ == "__main__":
    setup_database()