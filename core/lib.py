import random

from django.db import transaction
from faker import Faker
from rest_framework.authtoken.models import Token

from core.models import COUNTRIES, Player, Team, User

fake = Faker()


def get_random_country():
    country = random.choice(COUNTRIES)
    return country[0]


def create_player(fake, team, role):
    name = fake.name().split()
    first_name = name[0]
    last_name = ' '.join(name[1:])

    return Player.objects.create(
        team=team,
        role=role,
        first_name=first_name,
        last_name=last_name,
        country=get_random_country(),
        age=random.randint(20, 35),
    )


def generate_team(owner):
    with transaction.atomic():
        Team.objects.filter(owner=owner).delete()

        team = Team.objects.create(
            owner=owner,
            name=f"{fake.name()} United",
            country=get_random_country(),
        )

        for i in range(3):
            create_player(fake, team, Player.GOALKEEPER)

        for i in range(6):
            create_player(fake, team, Player.DEFENDER)

        for i in range(6):
            create_player(fake, team, Player.MIDFIELDER)

        for i in range(5):
            create_player(fake, team, Player.ATTACKER)


def generate_league(owners=30):
    for i in range(owners):
        email = fake.email()
        owner = User.objects.create_user(
            username=email,
            email=email,
            password='123',
        )

        Token.objects.get_or_create(user=owner)
        generate_team(owner)
