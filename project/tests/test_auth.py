import json

from project import db
from project.api.models import User
from project.tests.base import BaseTestCase
from project.tests.utils import add_user


class TestAuthBlueprint(BaseTestCase):
	
	def test_user_registration(self):
		with self.client:
			response = self.client.post(
				'/auth/register',
				data=json.dumps(dict(
					username='justatest',
					email='test@test.com',
					password='123456'
				)),
				content_type='application/json'
			)
			data = json.loads(response.data.decode())
			self.assertTrue(data['status'] == 'success')
			self.assertTrue(data['message'] == 'Successfully registered.')
			self.assertTrue(data['auth_token'])
			self.assertTrue(response.content_type == 'application/json')
			self.assertEqual(response.status_code, 201)