from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import UserProfileView

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    # path('subscription-plans/', UserProfileView.as_view(), name='user_profile'),
    # path('subscription-plan-detail/', UserProfileView.as_view(), name='user_profile'),
    # path('user-subscriptions/{user_id}/', UserProfileView.as_view(), name='user_profile'),
]
