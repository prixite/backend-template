import hashlib

import pycountry
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _

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
        path = reverse(
            'user-complete-email-verification',
            args=[self.user.id, code],
        )
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
