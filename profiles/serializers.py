from rest_framework import serializers
from .models import Profile

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)

    class Meta:
        model = Profile
        fields = ["id", "display_name", "email", "avatar"]

    def validate_display_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Display name is required.")
        return value