from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Project, Bug

app = Flask(__name__)
app.config["SECRET_KEY"] = "super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///bugtracker.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid credentials")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for("register"))
        role = "admin" if username.lower() == "admin" else "user"
        new_user = User(username=username, email=email, password=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("dashboard"))
    return render_template("register.html")

# --- THE CRITICAL DASHBOARD ROUTE ---
@app.route("/dashboard")
@login_required
def dashboard():
    # 1. Get Data
    bugs = Bug.query.order_by(Bug.status.desc()).all()
    projects = Project.query.all()

    # 2. CALCULATE STATS
    high = Bug.query.filter_by(priority='High').count()
    medium = Bug.query.filter_by(priority='Medium').count()
    low = Bug.query.filter_by(priority='Low').count()

    # 3. Send to HTML
    return render_template("dashboard.html", bugs=bugs, projects=projects, 
                           high=high, medium=medium, low=low)

@app.route("/project/create", methods=["POST"])
@login_required
def create_project():
    if current_user.role != "admin":
        return redirect(url_for("dashboard"))
    name = request.form["name"]
    desc = request.form.get("description", "")
    db.session.add(Project(name=name, description=desc))
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/bug/create", methods=["POST"])
@login_required
def create_bug():
    project_id = request.form.get("project_id")
    if not project_id:
        flash("Please create a Project first!")
        return redirect(url_for("dashboard"))

    bug = Bug(
        title=request.form["title"],
        description=request.form["description"],
        priority=request.form["priority"],
        project_id=project_id,
        created_by=current_user.id
    )
    db.session.add(bug)
    db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/bug/resolve/<int:id>")
@login_required
def resolve_bug(id):
    bug = Bug.query.get(id)
    if bug:
        bug.status = "Resolved"
        db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/bug/delete/<int:id>")
@login_required
def delete_bug(id):
    if current_user.role == "admin":
        bug = Bug.query.get(id)
        if bug:
            db.session.delete(bug)
            db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(email="admin@test.com").first():
            admin = User(username="Admin", email="admin@test.com", password=generate_password_hash("admin123"), role="admin")
            db.session.add(admin)
            db.session.commit()
    app.run(debug=True)