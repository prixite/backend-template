from unittest.mock import patch

from django.core import mail
from django.shortcuts import reverse
from faker import Faker
from rest_framework.authtoken.models import Token

from core.lib import generate_team
from core.models import SIGNUP_USER, Player, Team, Transfer, User
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

        url = reverse('team-list')
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

    def test_generate_action(self):
        self.login_admin()

        user = User.objects.get(email=self.user)

        self.assertEqual(Team.objects.all().count(), 0)
        self.assertEqual(Player.objects.all().count(), 0)

        url = reverse('user-generate', args=[user.id])
        response = self.post_json(url)
        self.assertOK(response)

        self.assertEqual(Team.objects.all().count(), 1)
        self.assertEqual(Player.objects.all().count(), 20)

        team = Team.objects.all().first()
        self.assertEqual(team.owner, user)

    def test_send_link_action(self):
        self.login_admin()
        user = User.objects.get(email=self.user)
        self.assertEqual(len(mail.outbox), 0)
        url = reverse('user-send-link', args=[user.id])
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
        self.assertEqual(Team.objects.all().count(), 1)
        self.assertEqual(Player.objects.all().count(), 20)

        combination = {
            Player.GOALKEEPER: 3,
            Player.DEFENDER: 6,
            Player.MIDFIELDER: 6,
            Player.ATTACKER: 5,
        }

        for role, count in combination.items():
            self.assertEqual(Player.objects.filter(role=role).count(), count)

        for player in Player.objects.all():
            self.assertEqual(player.market_value, 1000000)

        for team in Team.objects.all():
            self.assertEqual(team.value, 20 * 1000000)
            self.assertEqual(team.bank_balance, 5000000)

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
        self.assertEqual(Team.objects.all().count(), 1)
        self.assertEqual(Player.objects.all().count(), 20)


class PlayerTestCase(BaseTestCase):
    def test_sell_success(self):
        owner = self.login_user()
        generate_team(owner)
        player = Player.objects.all().first()
        data = {
            'fee': player.market_value,
        }
        url = reverse('player-sell', args=[player.id])
        response = self.post_json(url, data)

        self.assertOK(response)
        self.assertEqual(Transfer.objects.all().count(), 1)

        transfer = Transfer.objects.all().first()
        self.assertEqual(transfer.fee, player.market_value)

    def test_sell_with_admin_success(self):
        self.login_admin()

        owner = User.objects.get(username=self.user)
        generate_team(owner)
        player = Player.objects.all().first()
        data = {
            'fee': player.market_value,
        }
        url = reverse('player-sell', args=[player.id])
        response = self.post_json(url, data)

        self.assertOK(response)
        self.assertEqual(Transfer.objects.all().count(), 1)

        transfer = Transfer.objects.all().first()
        self.assertEqual(transfer.fee, player.market_value)

    def test_sell_failure(self):
        owner = User.objects.get(username=self.user)
        generate_team(owner)
        player = Player.objects.all().first()
        data = {
            'fee': player.market_value,
        }
        url = reverse('player-sell', args=[player.id])
        response = self.post_json(url, data)
        self.assertEqual(response.status_code, 401)

    def test_sell_failure_none_team(self):
        player = Player.objects.create(
            first_name='first',
            last_name='last',
            country='PK',
            age=20,
        )

        data = {
            'fee': 0,
        }
        url = reverse('player-sell', args=[player.id])
        response = self.post_json(url, data)
        self.assertEqual(response.status_code, 401)

    def test_sell_invalid_user_failure(self):
        self.login(self.signup_user)

        owner = User.objects.get(username=self.user)
        generate_team(owner)
        player = Player.objects.all().first()
        data = {
            'fee': player.market_value,
        }
        url = reverse('player-sell', args=[player.id])
        response = self.post_json(url, data)
        self.assertEqual(response.status_code, 403)

    def test_buy_success(self):
        new_owner = self.login(self.admin)

        owner = User.objects.get(username=self.user)

        generate_team(owner)
        generate_team(new_owner)

        player = owner.team.players.first()

        trade_amount = player.market_value

        old_team = owner.team
        new_team = new_owner.team

        old_team_balance = owner.team.bank_balance
        new_team_balance = new_owner.team.bank_balance

        transfer = Transfer.objects.create(
            player=player,
            fee=player.market_value,
        )

        url = reverse('player-buy', args=[player.id])
        data = {'team': new_owner.team.id}
        response = self.post_json(url, data=data)

        self.assertOK(response)

        transfer.refresh_from_db()
        self.assertFalse(transfer.is_active)

        old_team.refresh_from_db()
        new_team.refresh_from_db()

        self.assertEqual(
            old_team_balance + trade_amount,
            old_team.bank_balance,
        )

        self.assertEqual(
            new_team_balance - trade_amount,
            new_team.bank_balance,
        )

        player.refresh_from_db()
        self.assertTrue(player.market_value > trade_amount)

    def test_buy_404(self):
        owner = self.login_user()
        generate_team(owner)

        old_owner = User.objects.get(username=self.signup_user)
        generate_team(old_owner)

        player = old_owner.team.players.first()

        Transfer.objects.create(
            player=player,
            fee=player.market_value,
            is_active=False,
        )

        url = reverse('player-buy', args=[player.id])
        data = {
            'team': owner.team.id,
        }
        response = self.post_json(url, data=data)

        self.assertEqual(response.status_code, 404)

        Transfer.objects.all().delete()
        response = self.post_json(url, data=data)

        self.assertEqual(response.status_code, 404)

    def test_buy_negative_balance(self):
        owner = self.login_user()
        generate_team(owner)
        owner.team.bank_balance = 0
        owner.team.save()

        old_owner = User.objects.get(username=self.signup_user)
        generate_team(old_owner)

        player = old_owner.team.players.first()

        Transfer.objects.create(
            player=player,
            fee=player.market_value,
        )

        url = reverse('player-buy', args=[player.id])
        data = {
            'team': owner.team.id,
        }
        response = self.post_json(url, data=data)
        self.assertEqual(response.status_code, 400)

    def test_put_admin(self):
        self.login_admin()
        player = Player.objects.create(
            role=Player.ATTACKER,
            first_name='John',
            last_name='Doe',
            country='PK',
            age=30,
            market_value=100,
        )

        url = reverse('player-detail', args=[player.id])
        data = dict(
            role=Player.DEFENDER,
            first_name='Umair',
            last_name='Khan',
            country='US',
            age=40,
            market_value=0,
        )
        response = self.put_json(url, data=data)
        self.assertOK(response)

        player.refresh_from_db()
        self.assertEqual(player.age, 40)
        self.assertEqual(player.market_value, 0)
        self.assertEqual(player.first_name, 'Umair')
        self.assertEqual(player.last_name, 'Khan')

    def test_put_auth(self):
        owner = self.login_user()
        generate_team(owner)
        player = owner.team.players.first()

        player.market_value = 100
        player.age = 30
        player.save()

        url = reverse('player-detail', args=[player.id])
        data = dict(
            role=Player.DEFENDER,
            first_name='Umair',
            last_name='Khan',
            country='US',
            age=40,
            market_value=0,
        )
        response = self.put_json(url, data=data)
        self.assertOK(response)

        player.refresh_from_db()

        self.assertEqual(player.age, 30)
        self.assertEqual(player.market_value, 100)
        self.assertEqual(player.first_name, 'Umair')
        self.assertEqual(player.last_name, 'Khan')


class TransferTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.owner = User.objects.get(email=self.user)

        team = self.team = Team.objects.create(
            owner=self.owner,
            name='Test United',
            country='PK',
        )

        player = self.player = Player.objects.create(
            team=team,
            age=30,
            country='PK',
            first_name="Umair",
            last_name="Khan",
        )

        self.transfer = Transfer.objects.create(
            player=player,
            fee=player.market_value,
        )

    def test_admin_view(self):
        self.login_admin()
        response = self.client.get(reverse('transfer-list'))
        self.assertOK(response)

        data = response.json()
        self.assertEqual(data['count'], 1)

    def test_user_view(self):
        self.login_user()
        response = self.client.get(reverse('transfer-list'))
        self.assertOK(response)

        data = response.json()
        self.assertEqual(data['count'], 1)

    def test_country_filter(self):
        self.login_admin()
        url = reverse('transfer-list')
        url = f"{url}?country=pk"
        response = self.client.get(url)
        self.assertOK(response)

        data = response.json()
        self.assertEqual(data['count'], 1)

        url = reverse('transfer-list')
        url = f"{url}?country=none"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['count'], 0)

    def test_name_filter(self):
        self.login_admin()
        url = reverse('transfer-list')
        response = self.client.get(f"{url}?first_name=Umair")
        self.assertOK(response)

        data = response.json()
        self.assertEqual(data['count'], 1)

        response = self.client.get(f"{url}?last_name=Khan")
        self.assertOK(response)

        data = response.json()
        self.assertEqual(data['count'], 1)

        url = reverse('transfer-list')
        url = f"{url}?first_name=Invalid"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['count'], 0)

    def test_team_filter(self):
        self.login_admin()
        url = reverse('transfer-list')
        url = f"{url}?team=test united"
        response = self.client.get(url)
        self.assertOK(response)

        data = response.json()
        self.assertEqual(data['count'], 1)

        url = reverse('transfer-list')
        url = f"{url}?team=Invalid"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['count'], 0)

    def test_value_filter(self):
        self.login_admin()
        url = reverse('transfer-list')
        url = f"{url}?value={self.player.market_value}"
        response = self.client.get(url)
        self.assertOK(response)

        data = response.json()
        self.assertEqual(data['count'], 1)

        url = reverse('transfer-list')
        url = f"{url}?value=100"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['count'], 0)

    def test_multiple_filter(self):
        self.login_admin()
        url = reverse('transfer-list')
        url = f"{url}?value={self.player.market_value}"
        url = f"{url}&team=test united"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(data['count'], 1)


class TeamTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.owners = []

        for i in range(5):
            email = fake.email()

            owner = User.objects.create_user(
                username=email,
                email=email,
                password='123',
            )

            self.owners.append(owner)

            Team.objects.create(
                name=fake.name(),
                country='PK',
                owner=owner,
            )

    def test_list_admin(self):
        self.login_admin()
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertOK(response)
        data = response.json()
        self.assertEqual(data['count'], 5)

    def test_list_auth(self):
        self.login(self.owners[0].email)
        url = reverse('team-list')
        response = self.client.get(url)
        self.assertOK(response)
        data = response.json()
        self.assertEqual(data['count'], 1)

    def test_put_admin(self):
        self.login_admin()
        team = Team.objects.get(owner=self.owners[0])
        url = reverse('team-detail', args=[team.id])
        data = {
            'owner': team.owner.id,
            'name': 'Lahore United',
            'country': 'US',
            'bank_balance': 0,
        }
        response = self.put_json(url, data=data)
        self.assertOK(response)
        data = response.json()

        self.assertEqual(data['name'], 'Lahore United')
        self.assertEqual(data['country'], 'US')
        self.assertEqual(data['bank_balance'], 0)

    def test_put_auth(self):
        owner = self.owners[0]
        self.login(owner.email)
        team = Team.objects.get(owner=owner)
        url = reverse('team-detail', args=[team.id])
        data = {
            'name': 'Lahore United',
            'country': 'US',
            'bank_balance': 0,
        }
        response = self.put_json(url, data=data)
        self.assertOK(response)
        data = response.json()

        self.assertEqual(data['name'], 'Lahore United')
        self.assertEqual(data['country'], 'US')
        self.assertEqual(data['bank_balance'], 5000000)


class PlayerListTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

        self.owners = []

        for i in range(2):
            email = fake.email()

            owner = User.objects.create_user(
                username=email,
                email=email,
                password='123',
            )

            self.owners.append(owner)

            generate_team(owner)

    def test_list_admin(self):
        self.login_admin()
        url = reverse('player-list')
        response = self.client.get(url)
        self.assertOK(response)
        data = response.json()
        self.assertEqual(data['count'], 40)

    def test_list_admin_filter(self):
        self.login_admin()
        team = self.owners[0].team
        url = reverse('player-list')
        response = self.client.get(f"{url}?team_id={team.id}")
        self.assertOK(response)
        data = response.json()
        self.assertEqual(data['count'], 20)

    def test_list_auth(self):
        self.login(self.owners[0].email)
        url = reverse('player-list')
        response = self.client.get(url)
        self.assertOK(response)
        data = response.json()
        self.assertEqual(data['count'], 20)
