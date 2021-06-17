from django.core.management import BaseCommand

from core.lib import generate_league
from core.models import DEFAULT_USERS, Player, Team, User


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Reset league',
        )
        parser.add_argument('--size', type=int, default=30)

    def handle(self, *args, **options):
        if options['reset']:
            User.objects.exclude(email__in=DEFAULT_USERS).delete()
            Team.objects.all().delete()
            Player.objects.all().delete()

        owners = options['size']
        generate_league(owners=owners)

        print("OK")
