import hashlib
import random

import pycountry
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMultiAlternatives
from django.db import models, transaction
from django.db.models import functions
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _
from rest_framework.generics import get_object_or_404

COUNTRIES = [(c.alpha_2, c.name) for c in pycountry.countries]

SIGNUP_USER = 'signup@example.com'

DEFAULT_USERS = [
    'admin@example.com',
    'signup@example.com',
    'owner@example.com',
]


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)

    def __str__(self):
        return self.username

    def send_verification_email(self):
        email_verification, _ = EmailVerification.objects.get_or_create(
            user=self,
            defaults={'code': EmailVerification.generate_code(self.email)},
        )
        email_verification.send_verification_link()

    def verify_email(self, key):
        self.email_verification.verify(key)


class Team(models.Model):
    owner = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='team',
    )
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=2, choices=COUNTRIES)
    bank_balance = models.PositiveIntegerField(default=5000000)

    class Meta:
        indexes = [
            models.Index(
                functions.Upper('name'),
                name='upper_name_index',
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def value(self):
        return sum(p.market_value for p in self.players.all())


class Player(models.Model):
    GOALKEEPER = 'goal-keeper'
    DEFENDER = 'defender'
    MIDFIELDER = 'mid-fielder'
    ATTACKER = 'attacker'

    ROLES = [
        (GOALKEEPER, 'Goalkeeper'),
        (DEFENDER, 'Defender'),
        (MIDFIELDER, 'Midfielder'),
        (ATTACKER, 'Attacker'),
    ]

    team = models.ForeignKey(
        'Team',
        on_delete=models.SET_NULL,
        related_name='players',
        null=True,
    )
    role = models.CharField(max_length=20, choices=ROLES)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    country = models.CharField(max_length=2, choices=COUNTRIES)
    age = models.PositiveSmallIntegerField()
    market_value = models.PositiveIntegerField(default=1000000)

    class Meta:
        indexes = [
            models.Index(
                functions.Upper('first_name'),
                name='upper_first_name_index',
            ),
            models.Index(
                functions.Upper('last_name'),
                name='upper_last_name_index',
            ),
            models.Index(
                fields=['country'],
                name='country_index',
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def buy(cls, player, new_team):
        player = cls.objects.select_for_update().filter(id=player.id)

        with transaction.atomic():
            player = player.get()

            transfers = player.transfers.filter(is_active=True)
            transfer = get_object_or_404(transfers.select_for_update())

            transfer.is_active = False
            transfer.save()

            transfer_fee = transfer.fee

            player.team.bank_balance += transfer_fee
            player.team.save()

            new_team.bank_balance -= transfer_fee
            new_team.save()

            value_increase = random.uniform(1.1, 2)
            player.market_value = int(player.market_value * value_increase)
            player.team = new_team
            player.save()

    def sell(self, fee=None):
        fee = fee or self.market_value
        with transaction.atomic():
            Transfer.objects.filter(
                player=self,
                is_active=True,
            ).update(is_active=False)

            Transfer.objects.create(player=self, fee=fee)


class Transfer(models.Model):
    player = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        related_name='transfers',
    )
    fee = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(
                fields=['fee'],
                name='fee_index',
            ),
        ]


class EmailVerification(models.Model):
    user = models.OneToOneField(
        'User',
        on_delete=models.CASCADE,
        related_name='email_verification',
    )
    is_verified = models.BooleanField(default=False)
    code = models.CharField(max_length=100)

    def __str__(self):
        return self.user.email

    @classmethod
    def generate_code(cls, key):
        return hashlib.md5(key.encode()).hexdigest()

    def send_verification_link(self):
        code = self.code
        path = reverse('user-verify', args=[self.user.id, code])
        link = f'http://{settings.DOMAIN}{path}'
        context = {
            'verification_link': link,
            'name': self.user.get_full_name() or self.user.username,
        }

        subject = 'Welcome to Fantasy Soccer League'
        html_message = render_to_string('email/welcome.html', context)
        plain_message = strip_tags(html_message)
        from_email = settings.DEFAULT_FROM_EMAIL
        to = self.user.email

        msg = EmailMultiAlternatives(subject, plain_message, from_email, [to])
        msg.attach_alternative(html_message, "text/html")
        msg.send()

    def verify(self, key):
        self.is_verified = key == self.code
        self.save()
