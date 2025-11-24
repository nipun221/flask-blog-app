from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime
import time
import sqlalchemy.exc

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key")

# ---- DB CONFIG ----
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    # fallback for local dev without Docker
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# ---- MODELS ----
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    posts = db.relationship("Post", backref="author", lazy=True)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)


# ---- AUTH HELPERS ----
def current_user():
    user_id = session.get("user_id")
    if user_id:
        return User.query.get(user_id)
    return None


# ---- ROUTES ----
@app.route("/")
def index():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template("index.html", posts=posts, user=current_user())


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Username and password are required.", "error")
            return redirect(url_for("signup"))

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("Username already taken.", "error")
            return redirect(url_for("signup"))

        user = User(
            username=username,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "error")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        flash("Logged in successfully.", "success")
        return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out.", "success")
    return redirect(url_for("index"))


@app.route("/post", methods=["POST"])
def create_post():
    user = current_user()
    if not user:
        flash("You must be logged in to post.", "error")
        return redirect(url_for("login"))

    title = request.form["title"].strip()
    body = request.form["body"].strip()

    if not title or not body:
        flash("Title and description are required.", "error")
        return redirect(url_for("index"))

    post = Post(title=title, body=body, user_id=user.id)
    db.session.add(post)
    db.session.commit()

    flash("Post created!", "success")
    return redirect(url_for("index"))

def init_db_with_retry(retries=10, delay=3):
    """Try to create tables, retrying while DB starts up."""
    last_error = None
    for i in range(retries):
        try:
            print(f"[init_db] Attempt {i+1}/{retries}...")
            with app.app_context():
                db.create_all()
            print("[init_db] DB is ready, tables created (or already exist).")
            return
        except sqlalchemy.exc.OperationalError as e:
            last_error = e
            print(f"[init_db] DB not ready yet: {e}. Retrying in {delay}s...")
            time.sleep(delay)
        except Exception as e:
            last_error = e
            print(f"[init_db] Unexpected error: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    # if all retries exhausted, crash container so it's obvious
    raise last_error


if __name__ == "__main__":
    init_db_with_retry()
    app.run(host="0.0.0.0", port=5000, debug=True)
