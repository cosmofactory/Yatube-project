from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.views import PasswordResetView, PasswordChangeView
from django.contrib.auth.views import PasswordChangeDoneView
from django.contrib.auth.views import PasswordResetDoneView
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib.auth.views import PasswordResetCompleteView
from django.urls import path
from . import views


app_name = 'users'


urlpatterns = [
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(r'signup/', views.SignUp.as_view(), name='signup'),
    path(
        r'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        r'password_reset/',
        PasswordResetView.
        as_view(template_name='users/password_reset_form.html'),
        name='password_reset_form'
    ),
    path(
        r'password_change/',
        PasswordChangeView.
        as_view(template_name='users/password_change_form.html'),
        name='password_change'
    ),
    path(
        r'password_change/done/',
        PasswordChangeDoneView.
        as_view(template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        r'password_reset/done/',
        PasswordResetDoneView.
        as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        r'reset/<uidb64>/<token>',
        PasswordResetConfirmView.
        as_view(template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        r'reset/done/',
        PasswordResetCompleteView.
        as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
]
