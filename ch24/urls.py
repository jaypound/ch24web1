"""
URL configuration for ch24 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib.auth.models import User
from django_otp.admin import OTPAdminSite
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

class OTPAdmin(OTPAdminSite):
   pass

admin_site = OTPAdmin(name='OTPAdmin')
admin_site.register(User)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('admin/', admin_site.urls),
    path('', include('ch24app.urls')),
    path('creators/', include('django.contrib.auth.urls')),
    path('creators/', include('creators.urls')),
#     path(
#         'password_reset/',
#         auth_views.PasswordResetView.as_view(
#             template_name='registration/password_reset_form.html',
#             email_template_name='registration/password_reset_email.html',
#             subject_template_name='registration/password_reset_subject.txt',
#             success_url=reverse_lazy('password_reset_done')
#         ),
#         name='password_reset'
#     ),
    
#     # Confirm reset link sent
#     path(
#         'password_reset/done/',
#         auth_views.PasswordResetDoneView.as_view(
#             template_name='registration/password_reset_done.html'
#         ),
#         name='password_reset_done'
#     ),
    
#     # Link from the email to reset the password
#     path(
#         'reset/<uidb64>/<token>/',
#         auth_views.PasswordResetConfirmView.as_view(
#             template_name='registration/password_reset_confirm.html',
#             success_url='/reset/done/'
#         ),
#         name='password_reset_confirm'
#     ),
    
#     # Confirmation that the password was changed
#     path(
#         'reset/done/',
#         auth_views.PasswordResetCompleteView.as_view(
#             template_name='registration/password_reset_complete.html'
#         ),
#         name='password_reset_complete'
#     ),
# ]
