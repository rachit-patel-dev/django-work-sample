from django.urls import path

from core.interface.users import views

app_name = "users"
urlpatterns = [
    # Onboarding (Signup + Login + Logout)
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    # Home
    path("", views.home, name="home"),
    # Email Verification
    path(
        "users/send-verification-email/<str:email>",
        views.send_verification_link_manually,
        name="send_verification_link",
    ),
    path(
        "users/email/verification/<str:encoded_user_id>/",
        views.user_email_verification,
        name="email_verification",
    ),
    # Reset Forgot Password
    path("password-reset/", views.PasswordResetView.as_view(), name="password_reset"),
    path(
        "reset-password-confirm/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    # 404
    path("page-not-found/", views.error_404_page_view, name="404"),
]
