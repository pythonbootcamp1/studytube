from rest_framework import serializers
from .models import Category, Tag


class CategorySerializer(serializers.ModelSerializer):
    """카테고리 Serializer"""

    videos_count = serializers.IntegerField(source='videos.count', read_only=True)

    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'icon',
            'videos_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'updated_at']

    def validate_name(self, value):
        """이름 검증"""
        if len(value) < 2:
            raise serializers.ValidationError('카테고리명은 2자 이상이어야 합니다.')
        return value


class CategoryCreateSerializer(serializers.ModelSerializer):
    """카테고리 생성 Serializer"""

    class Meta:
        model = Category
        fields = ['name', 'description', 'icon']

    def validate_name(self, value):
        """이름 검증"""
        if len(value) < 2:
            raise serializers.ValidationError('카테고리명은 2자 이상이어야 합니다.')
        return value


class TagSerializer(serializers.ModelSerializer):
    """태그 Serializer"""

    videos_count = serializers.IntegerField(source='videos.count', read_only=True)

    class Meta:
        model = Tag
        fields = [
            'id', 'name', 'slug', 'videos_count', 'created_at'
        ]
        read_only_fields = ['id', 'slug', 'created_at']

    def validate_name(self, value):
        """이름 검증"""
        if len(value) < 2:
            raise serializers.ValidationError('태그명은 2자 이상이어야 합니다.')
        return value


class TagCreateSerializer(serializers.ModelSerializer):
    """태그 생성 Serializer"""

    class Meta:
        model = Tag
        fields = ['name']

    def validate_name(self, value):
        """이름 검증"""
        if len(value) < 2:
            raise serializers.ValidationError('태그명은 2자 이상이어야 합니다.')
        return value
