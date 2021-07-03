from unittest.mock import patch

from django.core import mail
from django.shortcuts import reverse
from faker import Faker
from rest_framework.authtoken.models import Token

from core.models import SIGNUP_USER, User
from core.tasks import send_verification_email
from core.tests.base import BaseTestCase

fake = Faker()


class AuthTestCase(BaseTestCase):
    def test_login(self):
        self.login(SIGNUP_USER)
        data = dict(username='owner@example.com', password='soccer')
        response = self.post_json('/login/', data=data)

        data = response.json()
        token = data['token']

        token_obj = Token.objects.get(user__email='owner@example.com')
        self.assertEqual(token_obj.key, token)

    def test_token_auth(self):
        owner = User.objects.get(email='owner@example.com')
        token = self.create_token(owner)

        headers = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

        url = reverse('user-list')
        response = self.client.get(url, **headers)
        self.assertOK(response)


class UserTestCase(BaseTestCase):
    def test_list_admin(self):
        self.login_admin()
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertOK(response)
        data = response.json()
        self.assertEqual(data['count'], 3)

    def test_list_auth(self):
        self.login_user()
        url = reverse('user-list')
        response = self.client.get(url)
        self.assertOK(response)
        data = response.json()
        self.assertEqual(data['count'], 1)

    def test_put_auth(self):
        user = self.login_user()
        url = reverse('user-detail', args=[user.id])
        response = self.put_json(url, data={
            'first_name': "John",
            'last_name': 'Doe',
            'password': 'test123',
        })
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'John')

    def test_patch_user(self):
        user = self.login_user()
        url = reverse('user-detail', args=[user.id])
        response = self.patch_json(url, data={
            'first_name': "John",
        })
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'John')

    def test_patch_user_email_failure(self):
        owner = self.login_user()
        old_email = owner.email

        url = reverse('user-detail', args=[owner.id])
        data = {
            'email': 'new@example.com',
        }
        response = self.patch_json(url, data)
        self.assertOK(response)

        owner.refresh_from_db()
        self.assertEqual(owner.email, old_email)

    def test_patch_user_change_email_success(self):
        self.login_admin()

        owner = User.objects.get(email=self.user)

        url = reverse('user-detail', args=[owner.id])
        data = {
            'email': 'new@example.com',
        }
        response = self.patch_json(url, data)
        self.assertOK(response)

        owner.refresh_from_db()
        self.assertEqual(owner.email, 'new@example.com')

    def test_admin_action(self):
        self.login_admin()

        user = User.objects.get(email=self.user)

        url = reverse('user-admin', args=[user.id])
        response = self.post_json(url)
        self.assertOK(response)

        self.assertFalse(user.is_staff)
        user.refresh_from_db()
        self.assertTrue(user.is_staff)

    def test_send_link_action(self):
        self.login_admin()
        user = User.objects.get(email=self.user)
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('user-email', args=[user.id])
        response = self.post_json(url)
        self.assertOK(response)
        self.assertEqual(len(mail.outbox), 1)


class VerifyTestCase(BaseTestCase):
    def test_verify_success(self):
        self.login(SIGNUP_USER)
        email = 'test@example.com'
        data = {'email': email, 'password': 'test123'}

        with patch('core.serializers.send_verification_email.delay') as mock_delay:  # noqa
            def send_email(*args, **kwargs):
                user = User.objects.get(email=email)
                send_verification_email(user.id)

            mock_delay.side_effect = send_email

            with self.captureOnCommitCallbacks(execute=True):
                self.post_json(reverse('user-signup'), data)

        user = User.objects.get(email=email)
        self.assertFalse(user.email_verification.is_verified)

        code = user.email_verification.code
        verification_url = reverse('user-verify', args=[user.id, code])
        self.client.get(verification_url)

        user.email_verification.refresh_from_db()
        self.assertTrue(user.email_verification.is_verified)


class SignupTestCase(BaseTestCase):
    def test_signup_success(self):
        self.login(SIGNUP_USER)
        data = {
            'email': 'test@example.com',
            'password': 'test123',
        }
        response = self.post_json(reverse('user-signup'), data)
        self.assertOK(response)

        self.assertEqual(User.objects.all().count(), 4)

    def test_signup_failure(self):
        data = {
            'email': 'test@example.com',
            'password': 'test123',
        }
        response = self.post_json(reverse('user-signup'), data)
        self.assertEqual(response.status_code, 401)

    def test_signup_failure_non_admin(self):
        self.login_user()
        data = {
            'email': 'test@example.com',
            'password': 'test123',
        }
        response = self.post_json(reverse('user-signup'), data)
        self.assertEqual(response.status_code, 403)

    def test_signup_success_admin(self):
        self.login_admin()
        data = {
            'email': 'test@example.com',
            'password': 'test123',
        }
        response = self.post_json(reverse('user-signup'), data)
        self.assertOK(response)

        self.assertEqual(User.objects.all().count(), 4)
