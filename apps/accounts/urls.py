from django.urls import path
from django.contrib.auth import views as auth_views

from .views import SignUp
from .views import Activate

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path('signin/', auth_views.LoginView.as_view(template_name = 'accounts/registration/signin.html'), name='signin'),
    path('signout/', auth_views.LogoutView.as_view()),
    path('activate/<uidb64>/<token>/', Activate.as_view(), name='activate'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name = 'accounts/registration/password_reset_form.html', html_email_template_name = 'accounts/registration/password_reset_email.html', subject_template_name = 'accounts/registration/password_reset_subject.txt', from_email = 'EduMate Support<support@edumate.com>'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name = 'accounts/registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name = 'accounts/registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name = 'accounts/registration/password_reset_complete.html'), name='password_reset_complete'),
]