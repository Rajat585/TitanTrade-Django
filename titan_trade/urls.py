"""
URL configuration for titan_trade project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from stocks import views   # tumhare app ka naam stocks hai
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.urls import reverse_lazy


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path("dashboard/", login_required(views.dashboard, login_url='/login/'), name="dashboard"),

    # path("dashboard/", TemplateView.as_view(template_name="stocks/dashboard.html"), name="dashboard"),
    # path('login/', views.login_page, name='login'),
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about'),
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='forgot_password.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url=reverse_lazy('password_reset_done')
    ), name='forgot_password'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('register/', views.custom_register, name='register'),
    path("login/", views.custom_login, name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
    path("admin-panel/", views.admin_panel, name="admin_panel"),
    path("profile/", views.profile, name="profile"),
    path("delete-account/", views.delete_account, name="delete_account"),
    path("subscribe/", views.subscribe, name="subscribe"),

]



