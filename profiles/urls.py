from django.urls import path
from .views import ProfileMeView, AvatarUploadView

urlpatterns = [
    path('profile/me/', ProfileMeView.as_view(), name='profile-me'),
    path('profile/avatar/', AvatarUploadView.as_view(), name='profile-avatar'),
]
