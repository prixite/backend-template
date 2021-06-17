from django.shortcuts import reverse

from core.models import SIGNUP_USER, Player, Team, Transfer, User
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

    def test_send_link_unauth(self):
        url = reverse('user-send-link', args=[self.owner.id])
        response = self.post_json(url)
        self.assert401(response)

    def test_send_link_default(self):
        self.login(SIGNUP_USER)
        url = reverse('user-send-link', args=[self.owner.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_send_link_auth(self):
        self.login(self.owner.email)
        url = reverse('user-send-link', args=[self.owner.id])
        response = self.post_json(url)
        self.assertOK(response)

    def test_send_link_auth_different_user(self):
        self.login('owner@example.com')
        url = reverse('user-send-link', args=[self.owner.id])
        response = self.post_json(url)
        self.assert404(response)

    def test_send_link_admin(self):
        self.login('admin@example.com')
        url = reverse('user-send-link', args=[self.owner.id])
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

    def test_verify_unauth(self):
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse('user-verify', args=[self.owner.id, code])
        response = self.client.get(url)
        self.assertOK(response)

    def test_verify_default(self):
        self.login(SIGNUP_USER)
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse('user-verify', args=[self.owner.id, code])
        response = self.client.get(url)
        self.assertOK(response)

    def test_verify_auth(self):
        self.login(self.owner.email)
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse('user-verify', args=[self.owner.id, code])
        response = self.client.get(url)
        self.assertOK(response)

    def test_verify_admin(self):
        self.login('admin@example.com')
        self.owner.send_verification_email()
        code = self.owner.email_verification.code
        url = reverse('user-verify', args=[self.owner.id, code])
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

    def test_generate_unauth(self):
        url = reverse('user-generate', args=[self.owner.id])
        response = self.post_json(url)
        self.assert401(response)

    def test_generate_default(self):
        self.login(SIGNUP_USER)
        url = reverse('user-generate', args=[self.owner.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_generate_auth(self):
        self.login(self.owner.email)
        url = reverse('user-generate', args=[self.owner.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_generate_admin(self):
        self.login('admin@example.com')
        url = reverse('user-generate', args=[self.owner.id])
        response = self.post_json(url)
        self.assertOK(response)


class TeamTestCase(BaseTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='perm@example.com',
            username='perm@example.com',
            password='123',
        )

        self.team = Team.objects.create(
            owner=self.owner,
            name='Test United',
            country='PK',
        )

    def test_get_unauth(self):
        url = reverse('team-list')
        response = self.client.get(url)
        self.assert401(response)

        url = reverse('team-detail', args=[self.team.id])
        response = self.client.get(url)
        self.assert401(response)

    def test_get_default(self):
        self.login(SIGNUP_USER)

        url = reverse('team-list')
        response = self.client.get(url)
        self.assert403(response)

        url = reverse('team-detail', args=[self.team.id])
        response = self.client.get(url)
        self.assert403(response)

    def test_get_auth(self):
        self.login(self.owner.email)

        url = reverse('team-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('team-detail', args=[self.team.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_get_auth_different_owner(self):
        self.login('owner@example.com')
        url = reverse('team-detail', args=[self.team.id])
        response = self.client.get(url)
        self.assert404(response)

    def test_get_admin(self):
        self.login('admin@example.com')

        url = reverse('team-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('team-detail', args=[self.team.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_post_unauth(self):
        url = reverse('team-list')
        data = {'name': 'Titans'}
        response = self.post_json(url, data=data)
        self.assert401(response)

    def test_post_default(self):
        self.login(SIGNUP_USER)
        url = reverse('team-list')
        data = {'name': 'Titans'}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_auth(self):
        self.login('owner@example.com')
        url = reverse('team-list')
        data = {'name': 'Titans'}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_admin(self):
        self.login('admin@example.com')
        owner = User.objects.get(email='owner@example.com')
        url = reverse('team-list')
        data = {'name': 'Titans', 'country': 'PK', 'owner': owner.id}
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_put_unauth(self):
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans'}
        response = self.put_json(url, data=data)
        self.assert401(response)

    def test_put_default(self):
        self.login(SIGNUP_USER)
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans'}
        response = self.put_json(url, data=data)
        self.assert403(response)

    def test_put_auth(self):
        self.login(self.owner.email)
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.put_json(url, data=data)
        self.assertOK(response)

    def test_put_auth_different_owner(self):
        self.login('owner@example.com')
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.put_json(url, data=data)
        self.assert404(response)

    def test_put_admin(self):
        self.login('admin@example.com')
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK', 'owner': self.owner.id}
        response = self.put_json(url, data=data)
        self.assertOK(response)

    def test_patch_unauth(self):
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assert401(response)

    def test_patch_default(self):
        self.login(SIGNUP_USER)
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assert403(response)

    def test_patch_auth(self):
        self.login(self.owner.email)
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assertOK(response)

    def test_patch_auth_different_owner(self):
        self.login('owner@example.com')
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assert404(response)

    def test_patch_admin(self):
        self.login('admin@example.com')
        url = reverse('team-detail', args=[self.team.id])
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assertOK(response)

    def test_delete_unauth(self):
        url = reverse('team-detail', args=[self.team.id])
        response = self.client.delete(url)
        self.assert401(response)

    def test_delete_default(self):
        self.login(SIGNUP_USER)
        url = reverse('team-detail', args=[self.team.id])
        response = self.client.delete(url)
        self.assert403(response)

    def test_delete_auth(self):
        self.login(self.owner.email)
        url = reverse('team-detail', args=[self.team.id])
        response = self.client.delete(url)
        self.assert403(response)

    def test_delete_admin(self):
        self.login('admin@example.com')
        url = reverse('team-detail', args=[self.team.id])
        response = self.client.delete(url)
        self.assertOK(response)

    def test_rank_unauth(self):
        url = reverse('team-rank')
        response = self.client.get(url)
        self.assert401(response)

    def test_rank_default(self):
        self.login(SIGNUP_USER)
        url = reverse('team-rank')
        response = self.client.get(url)
        self.assertOK(response)

    def test_rank_auth(self):
        self.login(self.owner.email)
        url = reverse('team-rank')
        response = self.client.get(url)
        self.assertOK(response)

    def test_rank_admin(self):
        self.login('admin@example.com')
        url = reverse('team-rank')
        response = self.client.get(url)
        self.assertOK(response)


class PlayerTestCase(BaseTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='perm@example.com',
            username='perm@example.com',
            password='123',
        )

        team = self.team = Team.objects.create(
            owner=self.owner,
            name='Test United',
            country='PK',
        )

        self.player = Player.objects.create(
            team=team,
            age=30,
            country='PK',
        )

    def test_get_unauth(self):
        url = reverse('player-list')
        response = self.client.get(url)
        self.assert401(response)

        url = reverse('player-detail', args=[self.player.id])
        response = self.client.get(url)
        self.assert401(response)

    def test_get_default(self):
        self.login(SIGNUP_USER)

        url = reverse('player-list')
        response = self.client.get(url)
        self.assert403(response)

        url = reverse('player-detail', args=[self.player.id])
        response = self.client.get(url)
        self.assert403(response)

    def test_get_auth(self):
        self.login(self.owner.email)

        url = reverse('player-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('player-detail', args=[self.player.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_get_admin(self):
        self.login('admin@example.com')

        url = reverse('player-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('player-detail', args=[self.player.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_post_unauth(self):
        url = reverse('player-list')
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.post_json(url, data=data)
        self.assert401(response)

    def test_post_default(self):
        self.login(SIGNUP_USER)
        url = reverse('player-list')
        data = {'name': 'Titans', 'country': 'PK'}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_auth(self):
        self.login('owner@example.com')
        url = reverse('player-list')
        data = {'country': 'PK'}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_admin(self):
        self.login('admin@example.com')

        url = reverse('player-list')
        data = {
            'country': 'PK',
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'role': 'attacker',
        }
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_put_unauth(self):
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK'}
        response = self.put_json(url, data=data)
        self.assert401(response)

    def test_put_default(self):
        self.login(SIGNUP_USER)
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK'}
        response = self.put_json(url, data=data)
        self.assert403(response)

    def test_put_auth(self):
        self.login(self.owner.email)
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK', 'first_name': 'John', 'last_name': 'Doe'}
        response = self.put_json(url, data=data)
        self.assertOK(response)

    def test_put_auth_other_owner(self):
        self.login('owner@example.com')
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK', 'first_name': 'John', 'last_name': 'Doe'}
        response = self.put_json(url, data=data)
        self.assert404(response)

    def test_put_admin(self):
        self.login('admin@example.com')

        url = reverse('player-detail', args=[self.player.id])
        data = {
            'country': 'PK',
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 40,
            'role': 'attacker',
        }
        response = self.put_json(url, data=data)
        self.assertOK(response)

    def test_patch_unauth(self):
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assert401(response)

    def test_patch_default(self):
        self.login(SIGNUP_USER)
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assert403(response)

    def test_patch_auth(self):
        self.login(self.owner.email)
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assertOK(response)

    def test_patch_auth_other_owner(self):
        self.login('owner@example.com')
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assert404(response)

    def test_patch_admin(self):
        self.login('admin@example.com')
        url = reverse('player-detail', args=[self.player.id])
        data = {'country': 'PK'}
        response = self.patch_json(url, data=data)
        self.assertOK(response)

    def test_delete_unauth(self):
        url = reverse('player-detail', args=[self.player.id])
        response = self.client.delete(url)
        self.assert401(response)

    def test_delete_default(self):
        self.login(SIGNUP_USER)
        url = reverse('player-detail', args=[self.player.id])
        response = self.client.delete(url)
        self.assert403(response)

    def test_delete_auth(self):
        self.login(self.owner.email)
        url = reverse('player-detail', args=[self.player.id])
        response = self.client.delete(url)
        self.assert403(response)

    def test_delete_admin(self):
        self.login('admin@example.com')
        url = reverse('player-detail', args=[self.player.id])
        response = self.client.delete(url)
        self.assertOK(response)

    def test_sell_unauth(self):
        url = reverse('player-sell', args=[self.player.id])
        response = self.post_json(url)
        self.assert401(response)

    def test_sell_default(self):
        self.login(SIGNUP_USER)
        url = reverse('player-sell', args=[self.player.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_sell_auth(self):
        self.login(self.owner.email)
        url = reverse('player-sell', args=[self.player.id])
        data = {'fee': self.player.market_value}
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_sell_auth_other_owner(self):
        self.login('owner@example.com')
        url = reverse('player-sell', args=[self.player.id])
        data = {'fee': self.player.market_value}
        response = self.post_json(url, data=data)
        self.assert404(response)

    def test_sell_admin(self):
        self.login('admin@example.com')
        url = reverse('player-sell', args=[self.player.id])
        data = {'fee': self.player.market_value}
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_buy_unauth(self):
        url = reverse('player-buy', args=[self.player.id])
        response = self.post_json(url)
        self.assert401(response)

    def test_buy_default(self):
        self.login(SIGNUP_USER)
        url = reverse('player-buy', args=[self.player.id])
        response = self.post_json(url)
        self.assert403(response)

    def test_buy_auth(self):
        owner = self.login('owner@example.com')
        team = Team.objects.create(
            owner=owner,
            name='New Team United',
        )

        Transfer.objects.create(
            player=self.player,
            fee=self.player.market_value,
        )

        url = reverse('player-buy', args=[self.player.id])
        data = {'team': team.id}
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_buy_auth_same_team(self):
        self.login(self.owner.email)
        url = reverse('player-buy', args=[self.player.id])
        data = {'team': self.owner.team.id}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_buy_auth_other_team(self):
        new_owner = User.objects.create_user(
            username='new@example.com',
            email='new@example.com',
            password='123',
        )

        team = Team.objects.create(
            owner=new_owner,
            name='New Team United',
        )

        self.login(self.owner.email)
        url = reverse('player-buy', args=[self.player.id])
        data = {'team': team.id}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_buy_admin(self):
        self.login('admin@example.com')
        team = Team.objects.create(
            owner=User.objects.get(email='owner@example.com'),
            name='New Team United',
        )

        Transfer.objects.create(
            player=self.player,
            fee=self.player.market_value,
        )

        url = reverse('player-buy', args=[self.player.id])
        data = {'team': team.id}
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_move_unauth(self):
        url = reverse('player-move', args=[self.player.id])
        team = Team.objects.all().first()
        data = dict(team=team.id)
        response = self.post_json(url, data=data)
        self.assert401(response)

    def test_move_default(self):
        self.login(SIGNUP_USER)
        team = Team.objects.all().first()
        data = dict(team=team.id)
        url = reverse('player-move', args=[self.player.id])
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_move_auth(self):
        self.login('owner@example.com')
        team = Team.objects.all().first()
        data = dict(team=team.id)
        url = reverse('player-move', args=[self.player.id])
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_move_admin(self):
        self.login('admin@example.com')
        team = Team.objects.all().first()
        data = dict(team=team.id)
        url = reverse('player-move', args=[self.player.id])
        response = self.post_json(url, data=data)
        self.assertOK(response)


class TransferTestCase(BaseTestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='perm@example.com',
            username='perm@example.com',
            password='123',
        )

        team = self.team = Team.objects.create(
            owner=self.owner,
            name='Test United',
            country='PK',
        )

        player = self.player = Player.objects.create(
            team=team,
            age=30,
            country='PK',
        )

        self.transfer = Transfer.objects.create(
            player=player,
            fee=player.market_value,
        )

    def test_get_unauth(self):
        url = reverse('transfer-list')
        response = self.client.get(url)
        self.assert401(response)

        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.get(url)
        self.assert401(response)

    def test_get_default(self):
        self.login(SIGNUP_USER)

        url = reverse('transfer-list')
        response = self.client.get(url)
        self.assert403(response)

        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.get(url)
        self.assert403(response)

    def test_get_auth(self):
        self.login(self.owner.email)

        url = reverse('transfer-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_get_admin(self):
        self.login('admin@example.com')

        url = reverse('transfer-list')
        response = self.client.get(url)
        self.assertOK(response)

        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.get(url)
        self.assertOK(response)

    def test_post_unauth(self):
        url = reverse('transfer-list')
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.post_json(url, data=data)
        self.assert401(response)

    def test_post_default(self):
        self.login(SIGNUP_USER)
        url = reverse('transfer-list')
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_auth(self):
        self.login('owner@example.com')
        url = reverse('transfer-list')
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.post_json(url, data=data)
        self.assert403(response)

    def test_post_admin(self):
        self.login('admin@example.com')
        url = reverse('transfer-list')
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.post_json(url, data=data)
        self.assertOK(response)

    def test_put_unauth(self):
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.put_json(url, data=data)
        self.assert401(response)

    def test_put_default(self):
        self.login(SIGNUP_USER)
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.put_json(url, data=data)
        self.assert403(response)

    def test_put_auth(self):
        self.login(self.owner.email)
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.put_json(url, data=data)
        self.assert403(response)

    def test_put_admin(self):
        self.login('admin@example.com')
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.put_json(url, data=data)
        self.assertOK(response)

    def test_patch_unauth(self):
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.patch_json(url, data=data)
        self.assert401(response)

    def test_patch_default(self):
        self.login(SIGNUP_USER)
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.patch_json(url, data=data)
        self.assert403(response)

    def test_patch_auth(self):
        self.login(self.owner.email)
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.patch_json(url, data=data)
        self.assert403(response)

    def test_patch_admin(self):
        self.login('admin@example.com')
        url = reverse('transfer-detail', args=[self.transfer.id])
        data = {'player': self.player.id, 'fee': self.player.market_value}
        response = self.patch_json(url, data=data)
        self.assertOK(response)

    def test_delete_unauth(self):
        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.delete(url)
        self.assert401(response)

    def test_delete_default(self):
        self.login(SIGNUP_USER)
        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.delete(url)
        self.assert403(response)

    def test_delete_auth(self):
        self.login(self.owner.email)
        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.delete(url)
        self.assert403(response)

    def test_delete_admin(self):
        self.login('admin@example.com')
        url = reverse('transfer-detail', args=[self.transfer.id])
        response = self.client.delete(url)
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
