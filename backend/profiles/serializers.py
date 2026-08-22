from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile


from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    display_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        username = validated_data["username"]
        email = validated_data["email"]
        password = validated_data["password"]
        display_name = (
            validated_data.get("full_name")
            or validated_data.get("display_name")
            or username
        )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )
        profile = Profile.objects.create(
            user=user,
            display_name=display_name,
        )
        return profile

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "display_name": instance.display_name,
            "email": instance.user.email,
        }



class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "display_name", "email", "avatar"]

    def validate_display_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Display name is required.")
        return value