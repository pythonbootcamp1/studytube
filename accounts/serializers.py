from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """기본 사용자 Serializer"""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_premium',
            'profile_image', 'bio',
            'followers_count', 'following_count', 'videos_count',
            'date_joined'
        ]
        read_only_fields = [
            'id', 'followers_count', 'following_count', 'videos_count',
            'date_joined'
        ]


class UserRegistrationSerializer(serializers.ModelSerializer):
    """회원가입 Serializer"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'role', 'first_name', 'last_name', 'profile_image', 'bio'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'role': {'required': False},
            'profile_image': {'required': False},
            'bio': {'required': False},
        }

    def validate_email(self, value):
        """이메일 중복 확인"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('이미 사용 중인 이메일입니다.')
        return value

    def validate_username(self, value):
        """사용자명 중복 확인"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('이미 사용 중인 사용자명입니다.')
        return value

    def validate(self, attrs):
        """비밀번호 확인"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': '비밀번호가 일치하지 않습니다.'
            })

        # Django 기본 비밀번호 검증
        try:
            validate_password(attrs['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'password': list(e.messages)
            })

        return attrs

    def create(self, validated_data):
        """사용자 생성"""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')

        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """프로필 조회/수정 Serializer"""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'is_premium',
            'profile_image', 'bio', 'first_name', 'last_name',
            'followers_count', 'following_count', 'videos_count',
            'date_joined'
        ]
        read_only_fields = [
            'id', 'username', 'email', 'role',
            'followers_count', 'following_count', 'videos_count',
            'date_joined'
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """커스텀 JWT 토큰 Serializer"""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # 토큰에 추가 정보 포함
        token['username'] = user.username
        token['email'] = user.email
        token['role'] = user.role

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # 응답에 사용자 정보 포함
        data['user'] = UserSerializer(self.user).data

        return data


class ChangePasswordSerializer(serializers.Serializer):
    """비밀번호 변경 Serializer"""

    old_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """현재 비밀번호 확인"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('현재 비밀번호가 올바르지 않습니다.')
        return value

    def validate(self, attrs):
        """새 비밀번호 확인"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': '새 비밀번호가 일치하지 않습니다.'
            })

        # Django 기본 비밀번호 검증
        try:
            validate_password(attrs['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({
                'new_password': list(e.messages)
            })

        return attrs

    def save(self, **kwargs):
        """비밀번호 변경"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
