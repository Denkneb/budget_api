from django.urls import path, include

from user.views import (
    CheckResetCodeView,
    SetNewPasswordView,
    PasswordResetRequestView,
    UserSignUpView,
    JWTUserPayloadView,
)

# router = DefaultRouter(trailing_slash=True)
# router.register('profile', CandidateViewSet, 'profile')


urlpatterns = [
    path('get-self-info/', JWTUserPayloadView.as_view(), name='get-self-info'),
    path('check-code/', CheckResetCodeView.as_view(), name='check-code'),
    path('set-password/', SetNewPasswordView.as_view(), name='set-password'),
    path('reset-pass/', PasswordResetRequestView.as_view(), name='reset-pass'),
    path('sign-up/', UserSignUpView.as_view(), name='sign-up'),

    # path('', include(router.urls)),
]


