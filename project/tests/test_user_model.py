from project import db
from project.api.models import User
from project.tests.base import BaseTestCase

from sqlalchemy.exc import IntegrityError
from project.tests.utils import add_user


class TestUserModel(BaseTestCase):

	def test_add_user(self):
		"""Ensure a user is added correctly."""
		user = add_user(
			username='justatest',
			email='test@test.com'
			)
		self.assertTrue(user.id)
		self.assertEqual(user.username, 'justatest')
		self.assertEqual(user.email, 'test@test.com')
		self.assertTrue(user.active)
		self.assertTrue(user.created_at)

	def test_add_user_duplicate_username(self):
		"""Ensure adding duplicate usernames raises IntegrityError."""
		user = add_user(
			username='justatest',
			email='test@test.com'
			)
		# can't use add_user helper function here because we need to pass
		# db.session.commit to the assertRaises function
		duplicate_user = User(
			username='justatest',
			email='test@test2.com'
			)
		db.session.add(duplicate_user)
		self.assertRaises(IntegrityError, db.session.commit)

	def test_add_user_duplicate_email(self):
		"""Ensure adding duplicate emails raises IntegrityError."""
		user = add_user(
			username='justatest',
			email='test@test.com'
			)
		duplicate_user = User(
			username='justanothertest',
			email='test@test.com'
			)
		db.session.add(duplicate_user)
		self.assertRaises(IntegrityError, db.session.commit)