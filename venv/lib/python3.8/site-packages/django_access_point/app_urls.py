from django.urls import path
from rest_framework.routers import DefaultRouter

from .auth import LoginView, ForgotPasswordView, ResetPasswordView, UserOnboardView
from .views import PlatformUser, PlatformUserCustomField, TenantUser, TenantUserCustomField

router = DefaultRouter()
router.register(r"platform/users/custom-fields",PlatformUserCustomField,basename="platform.user.custom-fields")
router.register(r"platform/users", PlatformUser, basename="platform.user")
router.register(r"tenant/users/custom-fields",TenantUserCustomField,basename="tenant.user.custom-fields")
router.register(r"tenant/users", TenantUser, basename="tenant.user")

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<str:token_payload>/', ResetPasswordView.as_view(), name='reset-password'),
    path('tenant-free-onboard/', UserOnboardView.as_view(), name='tenant-free-onboard'),
]

urlpatterns += router.urls
