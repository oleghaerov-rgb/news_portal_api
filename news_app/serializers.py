from django.contrib.auth.models import User
from rest_framework import serializers

from .models import News


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'password',
        ]
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True},
        }

    def validate_email(self, value):
        qs = User.objects.filter(email__iexact=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError('Пользователь с таким email уже существует.')
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': ['Это поле обязательно.']})
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class NewsSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = News
        fields = [
            'id',
            'title',
            'summary',
            'content',
            'author',
            'author_name',
            'date_created',
            'date_updated',
        ]
        read_only_fields = [
            'author',
            'author_name',
            'date_created',
            'date_updated',
        ]

    def validate_title(self, value):
        value = value.strip()
        if len(value) < 5:
            raise serializers.ValidationError('Минимум 5 символов.')
        return value

    def validate_summary(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError('Минимум 10 символов.')
        return value

    def validate_content(self, value):
        value = value.strip()
        if len(value) < 50:
            raise serializers.ValidationError('Минимум 50 символов.')
        return value
