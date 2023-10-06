from models import DEFAULT_IMAGE_URL, User, Post

from unittest import TestCase
import os

os.environ["DATABASE_URL"] = "postgresql:///blogly_test"
from app import app, db


# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        Post.query.delete()
        User.query.delete()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        db.session.add(test_user)
        db.session.commit()

        test_post = Post(title="test_post_title", content="test_post_content")

        test_user.posts.append(test_post)
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id
        self.post_id = test_post.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_list_users(self):
        """Test list users page"""

        with app.test_client() as c:
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_home_page(self):
        """Test home page"""

        with app.test_client() as c:
            # resp = c.get("/")

            # self.assertEqual(resp.status_code, 302)

            resp = c.get("/", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_user_page(self):
        """Test user page"""

        with app.test_client() as c:
            resp = c.get(f"/users/{self.user_id}")

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)
            self.assertIn(DEFAULT_IMAGE_URL, html)

    def test_add_new_user(self):
        """Test add new user"""

        with app.test_client() as c:
            data = {
                "first_name": "John",
                "last_name": "Snow",
                "image_url": ""
            }

            resp = c.post("/users/new", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("John", html)
            self.assertIn("Snow", html)

            # data = {
            #     "first_name": "John",
            #     "last_name": "Smith"
            # }

            # resp = c.post("/users/new", data=data, follow_redirects=True)

            # self.assertEqual(resp.status_code, 200)
            # html = resp.get_data(as_text=True)
            # self.assertIn("John", html)
            # self.assertIn("Smith", html)

    def test_delete_user(self):
        """Test delete user"""

        with app.test_client() as c:

            resp = c.post(f"/users/{self.user_id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertNotIn("test1_first", html)
            self.assertNotIn("test1_last", html)

class PostViewTestCase(TestCase):
    """Test views for posts."""

    def setUp(self):
        """Create test client, add sample data."""

        # As you add more models later in the exercise, you'll want to delete
        # all of their records before each test just as we're doing with the
        # User model below.
        Post.query.delete()
        User.query.delete()

        test_user = User(
            first_name="test1_first",
            last_name="test1_last",
            image_url=None,
        )

        db.session.add(test_user)
        db.session.commit()

        test_post = Post(title="test_post_title", content="test_post_content")

        test_user.posts.append(test_post)
        db.session.commit()

        # We can hold onto our test_user's id by attaching it to self (which is
        # accessible throughout this test class). This way, we'll be able to
        # rely on this user in our tests without needing to know the numeric
        # value of their id, since it will change each time our tests are run.
        self.user_id = test_user.id
        self.post_id = test_post.id

    def tearDown(self):
        """Clean up any fouled transaction."""
        db.session.rollback()

    def test_add_post(self):
        """Test add post"""

        with app.test_client() as c:
            data = {
                "title": "Bye",
                "content": "Bye"
            }

            resp = c.post(f"/users/{self.user_id}/posts/new", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Bye", html)
            self.assertIn("test_post_title", html)

    def test_delete_post(self):
        """Test delete post"""

        with app.test_client() as c:

            resp = c.post(f"/posts/{self.post_id}/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertNotIn("Hello", html)


    def test_post_form(self):
        """Test show form to add a post for this user"""

        with app.test_client() as c:
            resp = c.get(f"/users/{self.user_id}/posts/new")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test1_first", html)
            self.assertIn("test1_last", html)

    def test_show_a_post(self):
        """show a post"""
        # TODO:seperate to another test for failure test_show_a_post_invalid

        with app.test_client() as c:
            resp = c.get(f"/posts/{self.post_id}")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test_post_title", html)
            self.assertIn("test_post_content", html)

    def test_edit_post_form(self):
        """test the form to edit post"""

        with app.test_client() as c:
            resp = c.get(f"/posts/{self.post_id}/edit")

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("test_post_title", html)
            self.assertIn("test_post_content", html)

    def test_edit_post(self):
        """test edit post"""

        with app.test_client() as c:

            data = {
                "title": "Bye",
                "content": "Bye"
            }

            resp = c.post(f"/posts/{self.post_id}/edit", data=data, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn("Bye", html)
