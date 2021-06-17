import random

import requests
from django.conf import settings
from django.core.management import BaseCommand
from django.shortcuts import reverse

from core.models import SIGNUP_USER, Player, Team, User


def simulate(turns=50, error_probability=0.5, sell_probability=0.5):
    owners = User.objects.exclude(email=SIGNUP_USER)
    owners = owners.exclude(team__isnull=True)
    teams = Team.objects.all()
    players = Player.objects.all()

    for i in range(turns):
        owner = random.choice(owners)
        team = random.choice(teams)
        player = random.choice(players)

        sell = False
        if random.uniform(0, 1) > 1 - sell_probability:
            sell = True

        error_possible = False
        if random.uniform(0, 1) > 1 - error_probability:
            error_possible = True

        if sell and not error_possible:
            player = random.choice(list(owner.team.players.all()))
        elif not sell and not error_possible:
            team = random.choice(list(Team.objects.exclude(id=player.team.id)))
            owner = team.owner
            player.sell()

        headers = {
            'AUTHORIZATION': f'Bearer {owner.auth_token.key}',
        }

        if sell:
            path = reverse('player-sell', args=[player.id])
            url = f"http://{settings.DOMAIN}{path}"
            data = dict(fee=player.market_value)
            response = requests.post(url, headers=headers, data=data)
        else:
            path = reverse('player-buy', args=[player.id])
            url = f"http://{settings.DOMAIN}{path}"
            data = dict(team=team.id)
            response = requests.post(url, headers=headers, data=data)

        msg = ' - '.join([
            path,
            str(response.status_code),
            owner.email,
            f"Player value: {player.market_value}",
            f"Team balance: {team.bank_balance}",
            f"Expect error: {error_possible}",
        ])
        print(msg)


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--turns', type=int, default=50)
        parser.add_argument('--error-probability', type=float, default=0.5)
        parser.add_argument('--sell-probability', type=float, default=0.5)

    def handle(self, *args, **options):
        turns = options['turns']
        error_probability = options['error_probability']
        sell_probability = options['sell_probability']

        simulate(
            turns=turns,
            error_probability=error_probability,
            sell_probability=sell_probability,
        )
