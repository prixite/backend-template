from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import serializers

from core.models import User
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


class EmptySerializer(serializers.Serializer):
    pass
