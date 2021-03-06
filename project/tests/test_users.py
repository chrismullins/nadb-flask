import json
import datetime

from project import db
from project.api.models import User

from project.tests.base import BaseTestCase
from project.tests.utils import add_user

class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        """Ensure a new user can be added to the database."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data = json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com',
                    password='pass'
                    )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
                )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertIn('michael@realpython.com was added!', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown in the JSON object is empty."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown in the JSON object does not have a username key."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    email='michael@realpython.com',
                    password='pass'
                    )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_duplicate_email(self):
        """Ensure error is thrown in the email already exists."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com',
                    password='pass')),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com',
                    password='pass')),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn(
                'Sorry. That email already exists.', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user(self):
        """Ensure get single user behaves correctly."""
        user = add_user(username='michael', email='michael@realpython.com', password='pass')
        with self.client:
            response = self.client.get(f'/users/{user.id}')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertIn('michael', data['data']['username'])
            self.assertIn('michael@realpython.com', data['data']['email'])
            self.assertIn('success', data['status'])

    def test_single_user_no_id(self):
        """Ensure error is thrown if an id is not provided."""
        with self.client:
            response = self.client.get('/users/blah')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if the id does not exist."""
        with self.client:
            response = self.client.get('/users/999')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertIn('fail', data['status'])

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        # Create admin user
        add_user('admin', 'admin@admin.com', 'admin')
        user = User.query.filter_by(email='admin@admin.com').first()
        user.admin = True
        db.session.commit()
        created = datetime.datetime.utcnow() + datetime.timedelta(-30)
        add_user(username='michael',
                 email='michael@realpython.com',
                 password='pass',
                 created_at=created)
        add_user(username='fletcher',
                 email='fletcher@realpython.com',
                 password='pass')
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='admin@admin.com',
                    password='admin'
                )),
                content_type='application/json'
            )
            response = self.client.get(
                '/users',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                       resp_login.data.decode()
                   )['auth_token']
               )
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            # michael, fletcher, and the admin
            self.assertEqual(len(data['data']['users']), 3)
            self.assertTrue('created_at' in data['data']['users'][0])
            self.assertTrue('created_at' in data['data']['users'][1])
            # michael was created in the past, so he should be second in the list
            self.assertIn('michael', data['data']['users'][2]['username'])
            self.assertIn('fletcher', data['data']['users'][1]['username'])
            self.assertIn('michael@realpython.com', data['data']['users'][2]['email'])
            self.assertIn('fletcher@realpython.com', data['data']['users'][1]['email'])
            self.assertIn('success', data['status'])

    def test_add_user_invalid_json_keys_no_password(self):
        """Ensure error is thrown if the JSON object does not have a password key."""
        add_user('test', 'test@test.com', 'test')
        user = User.query.filter_by(email='test@test.com').first()
        user.admin = True
        db.session.commit()
        with self.client:
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data = json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com')),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload.', data['message'])
            self.assertIn('fail', data['status'])

    def test_add_user_not_admin(self):
        add_user('test', 'test@test.com', 'test')
        with self.client:
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='michael',
                    email='michael@realpython.com',
                    password='test'
                )),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(data['message'] == 'You do not have permission to do that.')
            self.assertEqual(response.status_code, 401)

    def test_deleted_user_is_gone(self):
        """Ensure deleted user is not there anymore."""
        # Create admin user
        add_user('admin', 'admin@admin.com', 'admin')
        user = User.query.filter_by(email='admin@admin.com').first()
        user.admin = True
        db.session.commit()
        # Create nonadmin user
        add_user('deleteme', 'deleteme@deleteme.com', 'deleteme')
        # login with admin user
        with self.client:
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='admin@admin.com',
                    password='admin'
                )),
                content_type='application/json'
            )
            deleteme_user = User.query.filter_by(email='deleteme@deleteme.com').first()
            response = self.client.delete(
                '/users/{}'.format(deleteme_user.id),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                    resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'success')
            self.assertTrue(data['message'] == 'User deleteme has been deleted.')
            self.assertEqual(response.status_code, 200)
            user = User.query.filter_by(email='deleteme@deleteme.com').first()
            self.assertIsNone(user)

    def test_delete_user_with_nonadmin_user(self):
        """Ensure that non-admin users get an error when trying to use this DELETE endpoint."""
        add_user('test', 'test@test.com', 'test')
        add_user('deleteme', 'deleteme@deleteme.com', 'deleteme')
        # login with admin user
        with self.client:
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='test@test.com',
                    password='test'
                )),
                content_type='application/json'
            )
            deleteme_user = User.query.filter_by(email='deleteme@deleteme.com').first()
            response = self.client.delete(
                '/users/{}'.format(deleteme_user.id),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            self.assertTrue(data['status'] == 'error')
            self.assertTrue(data['message'] == 'You do not have permissions to delete users.')
            self.assertEqual(response.status_code, 401)
            deleteme_user = User.query.filter_by(email='deleteme@deleteme.com').first()
            self.assertIsNotNone(deleteme_user)

    def test_delete_nonexistant_user(self):
        # Create admin user
        add_user('admin', 'admin@admin.com', 'admin')
        user = User.query.filter_by(email='admin@admin.com').first()
        user.admin = True
        db.session.commit()
        # Create nonadmin user
        add_user('deleteme', 'deleteme@deleteme.com', 'deleteme')
        # login with admin user
        with self.client:
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='admin@admin.com',
                    password='admin'
                )),
                content_type='application/json'
            )
            deleteme_user = User.query.filter_by(email='deleteme@deleteme.com').first()
            response = self.client.delete(
                '/users/{}'.format(deleteme_user.id),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            response_failed = self.client.delete(
                '/users/{}'.format(deleteme_user.id),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(
                        resp_login.data.decode()
                    )['auth_token']
                )
            )
            data = json.loads(response.data.decode())
            data_failed = json.loads(response_failed.data.decode())
            self.assertEqual(data['status'], 'success')
            self.assertEqual(data_failed['status'], 'fail')
            self.assertTrue(data_failed['message'] == 'User does not exist')
            self.assertEqual(response_failed.status_code, 404)

    def test_modify_user_as_admin(self):
        """Ensure admin user can modify users"""
        # Create admin user
        add_user('admin', 'admin@admin.com', 'admin')
        user = User.query.filter_by(email='admin@admin.com').first()
        user.admin = True
        db.session.commit()
        # Create nonadmin user
        add_user('changeme', 'changeme@changeme.com', 'changeme')
        # login with admin
        with self.client:
            # user login
            resp_login = self.client.post(
                '/auth/login',
                data=json.dumps(dict(
                    email='admin@admin.com',
                    password='admin'
                )),
                content_type='application/json'
            )
            changeme_user = User.query.filter_by(email='changeme@changeme.com').first()
            response = self.client.put(
                '/users/{}'.format(changeme_user.id),
                content_type='application/json',
                headers=dict(
                    Authorization='Bearer ' + json.loads(resp_login.data.decode())['auth_token']
                ),
                data=json.dumps(dict(
                    username='xchangeme',
                    email='changeme@changeme.com',
                    password='test'
                ))
            )
        response_data = json.loads(response.data.decode())
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['message'], 'Fields modified: username')