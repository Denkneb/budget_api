import logging

from django.contrib.auth.models import Permission
from django.contrib.auth.password_validation import validate_password as dj_validate_pasw
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from user.models import PasswordResetData, User

log = logging.getLogger('app')


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ('name', 'codename')


class JWTUserPayloadSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'is_superuser',
            'is_staff',
            'date_joined',
            'last_login',
            'phone_number',
            'first_name',
            'last_name'
        )


class RequestResetPassSerializer(serializers.Serializer):

    email = serializers.EmailField(allow_null=False, allow_blank=False)

    def create(self, validated_data):
        raise ValueError('Method not allowed')

    def update(self, instance, validated_data):
        raise ValueError('Method not allowed')


class CheckCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(allow_null=False, allow_blank=False)
    code = serializers.CharField(max_length=255, allow_blank=False, allow_null=False)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs.get('email'))
        except User.DoesNotExist:
            raise serializers.ValidationError(_('Invalid data presented'))

        hash_str = user.get_password_reset_hash(code=attrs.get('code'))
        if hash_str is None:
            raise serializers.ValidationError(_('Invalid data presented'))

        return attrs

    def create(self, validated_data) -> str:
        user = User.objects.get(email=validated_data.get('email'))
        hash_str = user.get_password_reset_hash(code=validated_data.get('code'))
        return hash_str

    def update(self, instance, validated_data):
        raise ValueError(_('Method not allowed'))


class RecoverySetNewPassword(serializers.Serializer):
    hash = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)
    password = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)
    confirm_password = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)

    def validate_password(self, value):
        try:
            dj_validate_pasw(value)
            return value
        except ValidationError as err:
            raise serializers.ValidationError(err)

    def validate_hash(self, value):
        try:
            password_reset_data = PasswordResetData.objects.get(hash_str=value)

            if not password_reset_data.is_active:
                raise serializers.ValidationError('Invalid hash')

            return value

        except PasswordResetData.DoesNotExist:
            raise serializers.ValidationError('Invalid hash')

    def create(self, validated_data) -> None:
        data = PasswordResetData.objects.get(hash_str=validated_data.get('hash'))
        data.complete(validated_data.get('password'))
        user = data.user
        return user

    def update(self, instance, validated_data):
        raise ValueError(_('Method not allowed'))


class UserProfileSignUpSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    password = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)
    confirm_password = serializers.CharField(max_length=255, allow_null=False, allow_blank=False)

    def validate_password(self, value):
        try:
            dj_validate_pasw(value)
            return value
        except ValidationError as err:
            raise serializers.ValidationError(err)

    def create(self, validated_data):
        raise ValueError('Method not allowed')

    def update(self, instance, validated_data):
        raise ValueError('Method not allowed')
