import logging

from django.db import transaction
from django.template import Context
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from user.models import User, FirebaseToken, Notification

log = logging.getLogger('app')


class AddUserSerializer(serializers.Serializer):
    email = serializers.ListField(child=serializers.EmailField())


class SimpleUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone_number',
            'first_name',
            'last_name',
        )
        read_only_fields = (
            'id',
            'email',
        )


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'phone_number',
            'first_name',
            'last_name',
            'is_active',
            'last_login',
            'date_joined',
        )
        read_only_fields = (
            'id',
            'is_active',
            'last_login',
            'date_joined',
        )


class CreateUserSerializer(UserSerializer):

    def create(self, validated_data):

        with transaction.atomic():
            user = super().create(validated_data)
            user.init_invite()

        return user


class UpdateUserSerializer(UserSerializer):
    email = serializers.EmailField(read_only=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        return super().update(instance, validated_data)


class InviteUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', )


class FirebaseTokenUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = FirebaseToken
        fields = ('token', )

    @transaction.atomic
    def create(self, validated_data):
        budget = self.context['request'].user
        firebase_token, created = FirebaseToken.objects.update_or_create(
            user=budget,
            defaults={
                'token': self.validated_data.get('token', None)
            }
        )
        return firebase_token

    def update(self, instance, validated_data):
        raise ValueError('Method not allowed')


class NotificationSerializer(serializers.ModelSerializer):

    user = UserSerializer(read_only=True)
    massage = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Notification
        fields = ('id', 'user', 'created', 'massage')

    @staticmethod
    def get_massage(obj):
        tmpl = User.get_template_push(obj.event)
        context = Context({
            'url': obj.mission.id,
            'datetime': obj.created,
        })
        return tmpl.format(context)
