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
			email='test@test.com',
			password='pass'
			)
		self.assertTrue(user.id)
		self.assertEqual(user.username, 'justatest')
		self.assertEqual(user.email, 'test@test.com')
		self.assertTrue(user.password)
		self.assertTrue(user.active)
		self.assertTrue(user.created_at)

	def test_add_user_duplicate_username(self):
		"""Ensure adding duplicate usernames raises IntegrityError."""
		user = add_user(
			username='justatest',
			email='test@test.com',
			password='pass'
			)
		# can't use add_user helper function here because we need to pass
		# db.session.commit to the assertRaises function
		duplicate_user = User(
			username='justatest',
			email='test@test2.com',
			password='pass'
			)
		db.session.add(duplicate_user)
		self.assertRaises(IntegrityError, db.session.commit)

	def test_add_user_duplicate_email(self):
		"""Ensure adding duplicate emails raises IntegrityError."""
		user = add_user(
			username='justatest',
			email='test@test.com',
			password='pass'
			)
		duplicate_user = User(
			username='justanothertest',
			email='test@test.com',
			password='pass'
			)
		db.session.add(duplicate_user)
		self.assertRaises(IntegrityError, db.session.commit)

	def test_passwords_are_random(self):
		user_one = add_user(
			username='justatest',
			email='test@test.com',
			password='test'
			)
		user_two = add_user(
			username='justatest2',
			email='test@test2.com',
			password='test'
			)
		self.assertNotEqual(user_one.password, user_two.password)

	def test_encode_auth_token(self):
		user = add_user(
			username='justatest',
			email='test@test.com',
			password='test'
			)
		auth_token = user.encode_auth_token(user.id)
		self.assertTrue(isinstance(auth_token, bytes))

	def test_decode_auth_token(self):
		user = add_user(
			username='justatest',
			email='test@test.com',
			password='test'
			)
		auth_token = user.encode_auth_token(user.id)
		self.assertTrue(isinstance(auth_token, bytes))
		self.assertEqual(User.decode_auth_token(auth_token), user.id)