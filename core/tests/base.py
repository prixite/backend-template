import json

from django.test import TestCase
from rest_framework.authtoken.models import Token

from core.models import User


class BaseTestCase(TestCase):
    def setUp(self):
        self.admin = 'admin@example.com'
        self.user = 'owner@example.com'
        self.signup_user = 'signup@example.com'

    def post_json(self, url, data=None):
        data = data or {}
        data = json.dumps(data)
        app_json = 'application/json'
        return self.client.post(url, data, content_type=app_json)

    def put_json(self, url, data=None):
        data = data or {}
        data = json.dumps(data)
        app_json = 'application/json'
        return self.client.put(url, data, content_type=app_json)

    def patch_json(self, url, data=None):
        data = data or {}
        data = json.dumps(data)
        app_json = 'application/json'
        return self.client.patch(url, data, content_type=app_json)

    def login_admin(self):
        admin = self.login(self.admin)
        return admin

    def login_user(self):
        return self.login(self.user)

    def login(self, username):
        user = User.objects.get(username=username)
        self.client.force_login(user)
        return user

    def create_token(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        return token.key

    def assertOK(self, response):
        self.assertEqual(response.status_code//100, 2)

    def assert401(self, response):
        self.assertEqual(response.status_code, 401)

    def assert403(self, response):
        self.assertEqual(response.status_code, 403)

    def assert404(self, response):
        self.assertEqual(response.status_code, 404)
