from django.contrib import admin

from .models import EmailVerification, Player, Team, Transfer, User

admin.site.register(EmailVerification)
admin.site.register(Player)
admin.site.register(Team)
admin.site.register(Transfer)
admin.site.register(User)
