from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Profile
from .serializers import ProfileSerializer
from .validators import validate_avatar

class ProfileMeView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        profile, created = Profile.objects.get_or_create(
            user=self.request.user,
            defaults={"display_name": self.request.user.username}
        )
        return profile


class AvatarUploadView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    serializer_class = ProfileSerializer

    def post(self, request, *args, **kwargs):
        profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={"display_name": request.user.username}
        )

        if 'avatar' not in request.FILES:
            return Response(
                {"avatar": ["No file provided."]},
                status=status.HTTP_400_BAD_REQUEST
            )

        avatar_file = request.FILES['avatar']

        try:
            validate_avatar(avatar_file)
        except DjangoValidationError as e:
            return Response(
                {"avatar": list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        profile.avatar = avatar_file
        profile.save()

        serializer = self.get_serializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

