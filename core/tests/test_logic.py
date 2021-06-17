from django.db.utils import IntegrityError

from core.models import Team, User
from core.tests.base import BaseTestCase


class TransferTestCase(BaseTestCase):
    def test_email_uniqueness(self):
        User.objects.create(username='one', email='email@example.com')
        with self.assertRaises(IntegrityError):
            User.objects.create(username='two', email='email@example.com')

    def test_user_can_have_only_team(self):
        user = User.objects.create(email='email@example.com')

        Team.objects.create(
            owner=user,
            name='Test',
            country='PK',
        )

        with self.assertRaises(IntegrityError):
            Team.objects.create(
                owner=user,
                name='Test',
                country='PK',
            )
