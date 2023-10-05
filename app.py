"""Blogly application."""

import os

from flask import Flask, render_template, redirect, request, flash
from models import db, connect_db, User, DEFAULT_IMAGE_URL, Post
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
    # pull by firstname or lastname or both, User.query.order_by().all()
    users = User.query.all()

    return render_template("users.html", users=users)


@app.get("/users/new")
def new_user_form():
    """render new user form"""

    return render_template("new-user-form.html")


@app.post("/users/new")
def add_new_user():
    """Adds new user"""

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"] or None

    new_user = User(
        first_name=first_name,
        last_name=last_name,
        image_url=image_url
    )

    db.session.add(new_user)
    db.session.commit()

    # try:
    #     db.session.commit()
    # except:
    #     flash(f"Invalid first or last name.")
    #     return redirect(f"/users/new?firstName={first_name}&lastName={last_name}&imageURL={image_url}")

    flash(f"Successfully added new user!")

    return redirect("/users")


@app.get("/users/<int:user_id>")
def user(user_id):
    """render user profile page"""

    user = User.query.get_or_404(user_id)

    return render_template("user.html", user=user)


@app.get("/users/<int:user_id>/edit")
def edit_user_form(user_id):
    """Show the edit page for a user"""

    user = User.query.get_or_404(user_id)

    return render_template("edit.html", user=user)


@app.post("/users/<int:user_id>/edit")
def edit_user(user_id):
    """Process the edit form, returning the user to the /users page."""

    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"]

    user = User.query.get_or_404(user_id)
    user.first_name = first_name
    user.last_name = last_name
    user.image_url = image_url if image_url else DEFAULT_IMAGE_URL

    db.session.commit()

    # try:
    #     db.session.commit()
    # except:
    #     flash(f"Invalid first or last name.")
    #     return redirect(f"/users/{user_id}/edit?firstName={first_name}&lastName={last_name}&imageURL={image_url}")

    flash("Successfully updated user profile!")

    return redirect(f"/users/{user_id}")


@app.post("/users/<int:user_id>/delete")
def delete_user(user_id):
    """Delete the user."""

    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return redirect('/users')


@app.get("/users/<int:user_id>/posts/new")
def new_post_form_handler(user_id):
    """Show form to add a post for that user."""

    user = User.query.get_or_404(user_id)

    return render_template("new-post-form.html", user=user)


@app.post("/users/<int:user_id>/posts/new")
def add_new_post(user_id):
    """Handle add form; add post and redirect to the user detail page."""

    title = request.form["title"]
    content = request.form["content"]

    user = User.query.get_or_404(user_id)
    post = Post(title=title, content=content, user_id=user.id)

    user.posts.append(post)

    db.session.commit()

    flash("New post successfully added!")

    return redirect(f"/users/{user_id}")


@app.get("/posts/<post_id>")
def show_a_post(post_id):
    """Show a post"""

    post = Post.query.get_or_404(post_id)

    return render_template('post.html', post=post)


@app.get("/posts/<post_id>/edit")
def edit_post_form(post_id):
    """Show form to edit a post, and to cancel (back to user page)."""

    post = Post.query.get_or_404(post_id)

    return render_template('edit-post-form.html', post=post)


@app.post("/posts/<post_id>/edit")
def edit_post(post_id):
    """Handle editing of a post. Redirect back to the post view."""

    title = request.form["title"]
    content = request.form["content"]

    post = Post.query.get_or_404(post_id)
    post.title = title
    post.content = content

    db.session.commit()

    flash(f"Post has been edited!")

    return redirect(f"/posts/{post_id}")


@app.post("/posts/<post_id>/delete")
def delete_post(post_id):
    """Delete the post."""

    post = Post.query.get_or_404(post_id)
    user_id = post.user.id

    db.session.delete(post)
    db.session.commit()

    flash(f"Post has been deleted!")

    return redirect(f"/users/{ user_id }")