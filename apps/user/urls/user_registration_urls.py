from django.urls import path
from apps.user.views.user_registration_view import (
    UserRegistrationCreateCodeView,
    UserVerifyCodeView,
    UserSetPasswordView,
    UserPasswordResetView, UserChangeInfoView
)

urlpatterns = [
    path("register/",UserRegistrationCreateCodeView.as_view(),name="register"),
    path("verify/",UserVerifyCodeView.as_view(),name="verify"),
    path("set-password/",UserSetPasswordView.as_view(),name="set_password"),
    path("reset-password/",UserPasswordResetView.as_view(),name="reset_password"),
    path("change-info/",UserChangeInfoView.as_view(),name="change_info"),

]