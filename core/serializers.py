from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import serializers

from core.lib import generate_team
from core.models import Player, Team, Transfer, User
from core.tasks import send_verification_email


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'url',
            'email',
            'password',
            'username',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['username']

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, user, validated_data):
        if 'email' in validated_data:
            validated_data['username'] = validated_data['email']

        if 'password' in validated_data:
            password = make_password(validated_data['password'])
            validated_data['password'] = password

        return super().update(user, validated_data)


class SignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'password',
            'first_name',
            'last_name',
            'email',
        ]

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        validated_data['password'] = make_password(validated_data['password'])
        with transaction.atomic():
            user = super().create(validated_data)
            generate_team(user)

        transaction.on_commit(lambda: send_verification_email.delay(user.id))

        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'url',
            'email',
            'password',
            'first_name',
            'last_name',
        ]
        read_only_fields = ['email']

    def update(self, user, validated_data):
        if 'password' in validated_data:
            password = make_password(validated_data['password'])
            validated_data['password'] = password

        return super().update(user, validated_data)


class TeamAdminSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(read_only=True)
    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = '__all__'

    def get_owner_email(self, obj):
        return obj.owner.email


class TeamSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(read_only=True)
    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = '__all__'
        read_only_fields = ['bank_balance', 'owner']

    def get_owner_email(self, obj):
        return obj.owner.email


class PlayerAdminSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = '__all__'

    def get_team_name(self, player):
        try:
            return player.team.name
        except Exception:
            return None


class PlayerSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()

    class Meta:
        model = Player
        fields = '__all__'
        read_only_fields = [
            'age',
            'market_value',
            'role',
            'team',
        ]

    def get_team_name(self, player):
        try:
            return player.team.name
        except Exception:
            return None


class TransferSerializer(serializers.ModelSerializer):
    player_data = serializers.SerializerMethodField()

    class Meta:
        model = Transfer
        fields = '__all__'

    def get_player_data(self, transfer):
        player = PlayerSerializer(transfer.player)
        return player.data


class PlayerSellSerializer(serializers.Serializer):
    fee = serializers.IntegerField()


class PlayerBuySerializer(serializers.Serializer):
    team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
    )


class AddPlayerToTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['team']


class EmptySerializer(serializers.Serializer):
    pass
