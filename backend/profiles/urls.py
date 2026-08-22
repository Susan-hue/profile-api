from django.urls import path
from .views import ProfileMeView, AvatarUploadView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='profile-register'),
    path('profile/register/', RegisterView.as_view(), name='profile-register-legacy'),
    path('profile/me/', ProfileMeView.as_view(), name='profile-me'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='profile-avatar'),
]

