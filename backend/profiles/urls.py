from django.urls import path
from .views import ProfileMeView, AvatarUploadView, RegisterView

urlpatterns = [
    path('profile/register/', RegisterView.as_view(), name='profile-register'),
    path('profile/me/', ProfileMeView.as_view(), name='profile-me'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='profile-avatar'),
]
