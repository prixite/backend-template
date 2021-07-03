from django.shortcuts import reverse

from core.models import SIGNUP_USER, User
from core.tests.base import BaseTestCase


class LoginTestCase(BaseTestCase):
    def test_get_unauth(self):
        data = dict(username='owner@example.com', password='soccer')
        response = self.post_json('/login/', data=data)
        self.assert401(response)

    def test_get_default(self):
        self.login(SIGNUP_USER)
        data = dict(username='owner@example.com', password='soccer')
        response = self.post_json('/login/', data=data)
        self.assertOK(response)

    def test_get_admin(self):
        self.login_admin()
        data = dict(username='owner@example.com', password='soccer')
        response = self.post_json('/login/', data=data)
        self.assert403(response)

    def test_get_auth(self):
        self.login_user()
        data = dict(username='admin@example.com', password='admin')
        response = self.post_json('/login/', data=data)
        self.assert403(response)


class UserTestCase(BaseTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='perm@example.com',
            username='perm@example.com',
            password='123',
        )

    def test_get_unauth(self):
        url = reverse('user-list')
        response = self.client.get(url)
        self.assert401(response)

        url = reverse('user-detail', args=[1])
        response = self.client.get(url)
        self.assert401(response)

    def test_get_default(self):
        self.login(SIGNUP_USER)

        url = reverse('user-list')
        response = self.client.get(url)
        self.assert403(response)

        url = reverse('user-detail', args=[1])
        response = self.client.get(url)
        self.assert403(response)

    def test_get_auth(self):
        self.login(self.owner.email)

        url = reverse('user-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('user-detail', args=[self.owner.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_get_auth_different_user(self):
        self.login('owner@example.com')

        url = reverse('user-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('user-detail', args=[self.owner.id])
        response = self.client.get(url)
        self.assert404(response)

    def test_get_admin(self):
        self.login('admin@example.com')

        url = reverse('user-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('user-detail', args=[self.owner.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_post_unauth(self):
        url = reverse('user-list')
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.post_json(url, data=data)
        self.assert401(response)

    def test_post_default(self):
        self.login(SIGNUP_USER)
        url = reverse('user-list')
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_auth(self):
        self.login('owner@example.com')
        url = reverse('user-list')
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_admin(self):
        self.login('admin@example.com')
        url = reverse('user-list')
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_put_unauth(self):
        url = reverse('user-detail', args=[self.owner.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.put_json(url, data=data)
        self.assert401(response)

    def test_put_default(self):
        user = self.login(SIGNUP_USER)
        url = reverse('user-detail', args=[user.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.put_json(url, data=data)
        self.assert403(response)

    def test_put_auth(self):
        self.login(self.owner.email)
        url = reverse('user-detail', args=[self.owner.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.put_json(url, data=data)
        self.assertOK(response)

    def test_put_admin(self):
        self.login('admin@example.com')
        url = reverse('user-detail', args=[self.owner.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.put_json(url, data=data)
        self.assertOK(response)

    def test_patch_unauth(self):
        url = reverse('user-detail', args=[self.owner.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.patch_json(url, data=data)
        self.assert401(response)

    def test_patch_default(self):
        user = self.login(SIGNUP_USER)
        url = reverse('user-detail', args=[user.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.patch_json(url, data=data)
        self.assert403(response)

    def test_patch_auth(self):
        self.login(self.owner.email)
        url = reverse('user-detail', args=[self.owner.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.patch_json(url, data=data)
        self.assertOK(response)

    def test_patch_admin(self):
        self.login('admin@example.com')
        url = reverse('user-detail', args=[self.owner.id])
        data = {'email': 'john@example.com', 'password': 'soccer'}
        response = self.patch_json(url, data=data)
        self.assertOK(response)

    def test_delete_unauth(self):
        owner = User.objects.get(username='owner@example.com')
        url = reverse('user-detail', args=[owner.id])
        response = self.client.delete(url)
        self.assert401(response)

    def test_delete_default(self):
        user = self.login(SIGNUP_USER)
        url = reverse('user-detail', args=[user.id])
        response = self.client.delete(url)
        self.assert403(response)

    def test_delete_auth(self):
        owner = self.login('owner@example.com')
        url = reverse('user-detail', args=[owner.id])
        response = self.client.delete(url)
        self.assertOK(response)

    def test_delete_admin(self):
        admin = self.login('admin@example.com')
        url = reverse('user-detail', args=[admin.id])
        response = self.client.delete(url)
        self.assertOK(response)

    def test_start_email_verification_unauth(self):
        url = reverse('user-start-email-verification', args=[self.owner.id])
        response = self.post_json(url)
        self.assert401(response)

    def test_start_email_verification_default(self):
        self.login(SIGNUP_USER)
        url = reverse('user-start-email-verification', args=[self.owner.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_start_email_verification_auth(self):
        self.login(self.owner.email)
        url = reverse('user-start-email-verification', args=[self.owner.id])
        response = self.post_json(url)
        self.assertOK(response)

    def test_start_email_verification_auth_different_user(self):
        self.login('owner@example.com')
        url = reverse('user-start-email-verification', args=[self.owner.id])
        response = self.post_json(url)
        self.assert404(response)

    def test_start_email_verification_admin(self):
        self.login('admin@example.com')
        url = reverse('user-start-email-verification', args=[self.owner.id])
        response = self.post_json(url)
        self.assertOK(response)

    def test_signup_unauth(self):
        url = reverse('user-signup')
        response = self.post_json(url)
        self.assert401(response)

    def test_signup_default(self):
        self.login(SIGNUP_USER)
        data = dict(email='new@example.com', password='123')
        url = reverse('user-signup')
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_signup_auth(self):
        self.login(self.owner.email)
        data = dict(email='new@example.com', password='123')
        url = reverse('user-signup')
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_signup_admin(self):
        self.login('admin@example.com')
        data = dict(email='new@example.com', password='123')
        url = reverse('user-signup')
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_complete_email_verification_unauth(self):
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse(
            'user-complete-email-verification',
            args=[self.owner.id, code],
        )
        response = self.client.get(url)
        self.assertOK(response)

    def test_complete_email_verification_default(self):
        self.login(SIGNUP_USER)
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse(
            'user-complete-email-verification',
            args=[self.owner.id, code],
        )
        response = self.client.get(url)
        self.assertOK(response)

    def test_complete_email_verification_auth(self):
        self.login(self.owner.email)
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse(
            'user-complete-email-verification',
            args=[self.owner.id, code],
        )
        response = self.client.get(url)
        self.assertOK(response)

    def test_complete_email_verification_admin(self):
        self.login('admin@example.com')
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse(
            'user-complete-email-verification',
            args=[self.owner.id, code],
        )
        response = self.client.get(url)
        self.assertOK(response)

    def test_admin_unauth(self):
        url = reverse('user-admin', args=[self.owner.id])
        response = self.post_json(url)
        self.assert401(response)

    def test_admin_default(self):
        self.login(SIGNUP_USER)
        url = reverse('user-admin', args=[self.owner.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_admin_auth(self):
        self.login(self.owner.email)
        url = reverse('user-admin', args=[self.owner.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_admin_admin(self):
        self.login('admin@example.com')
        url = reverse('user-admin', args=[self.owner.id])
        response = self.post_json(url)
        self.assertOK(response)


class CountryTestCase(BaseTestCase):
    def test_list_unauth(self):
        url = reverse('countries-list')
        response = self.client.get(url)
        self.assert401(response)

    def test_list_default(self):
        self.login(SIGNUP_USER)
        url = reverse('countries-list')
        response = self.client.get(url)
        self.assertOK(response)

    def test_list_auth(self):
        self.login('owner@example.com')
        url = reverse('countries-list')
        response = self.client.get(url)
        self.assertOK(response)

    def test_list_admin(self):
        self.login('admin@example.com')
        url = reverse('countries-list')
        response = self.client.get(url)
        self.assertOK(response)
