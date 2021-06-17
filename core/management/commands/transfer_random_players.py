import random

from django.core.management import BaseCommand

from core.models import Player


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        players = list(Player.objects.all())
        for i in range(50):
            index = random.randint(0, len(players)-1)
            player = players.pop(index)
            player.sell(player.market_value)
