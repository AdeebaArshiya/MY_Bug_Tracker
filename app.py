import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'soft-theme-local-time'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bugtracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- Models ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    bugs = db.relationship('Bug', backref='reporter', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    bugs = db.relationship('Bug', backref='project', lazy=True)

class Bug(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    priority = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Open')
    
    # FIXED: Changed from utcnow to now() for local time
    created_at = db.Column(db.DateTime, default=datetime.now) 
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)
    # FIXED: Changed from utcnow to now()
    timestamp = db.Column(db.DateTime, default=datetime.now)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Routes ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('username')).first()
        if user and user.password == request.form.get('password'):
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# FIX: Added missing register route to stop BuildError
@app.route('/register')
def register():
    return "Registration is currently restricted to Admin users."

@app.route('/dashboard')
@login_required
def dashboard():
    bugs = Bug.query.order_by(Bug.created_at.desc()).all()
    projects = Project.query.all()
    activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
    high = Bug.query.filter_by(priority='High', status='Open').count()
    med = Bug.query.filter_by(priority='Medium', status='Open').count()
    low = Bug.query.filter_by(priority='Low', status='Open').count()
    return render_template('dashboard.html', bugs=bugs, projects=projects, activities=activities, high=high, med=med, low=low)

# FIX: Added missing projects_page route to stop BuildError
@app.route('/projects')
@login_required
def projects_page():
    projects = Project.query.all()
    return render_template('projects.html', projects=projects)

@app.route('/settings')
@login_required
def settings_page():
    return render_template('settings.html')

@app.route('/create_bug', methods=['POST'])
@login_required
def create_bug():
    new_bug = Bug(
        title=request.form.get('title'),
        description=request.form.get('description'),
        priority=request.form.get('priority'),
        project_id=request.form.get('project_id'),
        user_id=current_user.id
    )
    db.session.add(new_bug)
    db.session.add(ActivityLog(content=f"🚀 {current_user.username} reported: {new_bug.title}"))
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/resolve/<int:id>')
@login_required
def resolve_bug(id):
    bug = Bug.query.get_or_404(id)
    bug.status = 'Resolved'
    # FIXED: Changed from utcnow() to now()
    bug.resolved_at = datetime.now() 
    db.session.add(ActivityLog(content=f"✅ {current_user.username} resolved: {bug.title}"))
    db.session.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Seed initial data if database is new
        if not User.query.filter_by(username='admin').first():
            db.session.add(User(username='admin', password='password123'))
        if not Project.query.first():
            db.session.add(Project(name="Default Project"))
        db.session.commit()
    app.run(debug=True)