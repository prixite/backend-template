import random

from core.models import COUNTRIES


def get_random_country():
    country = random.choice(COUNTRIES)
    return country[0]
