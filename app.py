"""Blogly application."""

import os

from flask import Flask, render_template, redirect, request
from models import db, connect_db, User
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    "DATABASE_URL", 'postgresql:///blogly')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)


@app.get("/")
def home():
    """redirects to /users page"""

    return redirect("/users")


@app.get("/users")
def users():
    """render all existing users to the home page"""

    users = User.query.all()

    return render_template("users.html", users=users)


@app.get("/users/new")
def new_user_form():
    """render new user form"""

    return render_template("new-user-form.html")


@app.post("/users/new")
def add_new_user():
    """Adds new user"""

    first_name = request.form.get("firstName")
    last_name = request.form.get("lastName")
    image_url = request.form.get("imageURL")

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        image_url=image_url
    )

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.get("/users/<int:user_id>")
def user(user_id):
    """render user profile page"""

    user = User.query.get_or_404(user_id)

    return render_template("user.html", user=user)


@app.get("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Show the edit page for a user"""

    user = User.query.get_or_404(user_id)

    return render_template("edit.html", user=user)


@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """Show the edit page for a user"""

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect('/users')
