from django.urls import path
from . import views
from .views import health_check, AvailableContentView
from django.contrib.auth import views as auth_views
from .forms import CreatorEmailPasswordResetForm
from django.urls import reverse_lazy
from django.urls import path
from .views import test_email
from django.views.generic.base import RedirectView
from django.urls import re_path
from .views import acme_challenge_view


urlpatterns = [
    path('', views.home, name="home"),
    path('creators/', views.all_creators, name="list-creators"),
    path('programs/', views.all_programs, name="list-programs"),
    path('episodes/', views.all_episodes, name="list-episodes"),
    path('my_creators/', views.my_creators, name="my-creators"),
    path('my_programs/', views.my_programs, name="my-programs"),
    path('my_episodes/', views.my_episodes, name="my-episodes"),
    path('add_creator/', views.add_creator, name="add-creator"),
    path('add_program/', views.add_program, name="add-program"),
    path('add_episode/', views.add_episode, name="add-episode"),
    path('update_creator/<creator_id>', views.update_creator, name="update-creator"),
    path('update_program/<program_id>', views.update_program, name="update-program"),
    path('update_episode/<episode_id>', views.update_episode, name="update-episode"),
    path('update_analysis/<str:custom_id>/', views.update_analysis, name='update-analysis'),
    path('upload_episode/<episode_id>/', views.upload_episode, name='upload_episode'),
    path('upload_success/', views.upload_success, name='upload_success'),
    path('upload_failed/', views.upload_failed, name='upload_failed'),
    path('upload_episode/<str:episode_id>/', views.upload_episode, name='upload_episode'),
    path('view_episode/<str:episode_id>/', views.view_episode, name='view_episode'),
    path('adobe_premiere/', views.adobe_premiere, name='adobe_premiere'),
    path('davinci_resolve/', views.davinci_resolve, name='davinci_resolve'),
    path('getting_started/', views.getting_started, name='getting_started'),
    # path('getting_started2/', views.getting_started2, name='getting_started2'),
    path('episode/<str:episode_id>/media_info/', views.episode_media_info, name='episode_media_info'),
    path('support/submit/', views.submit_ticket, name='submit_ticket'),
    path('support/submitted/<int:ticket_no>/', views.ticket_submitted, name='ticket_submitted'),
    path('support/ticket/<int:ticket_no>/', views.ticket_detail, name='ticket_detail'),
    path('support/my_tickets/', views.my_tickets, name='my_tickets'),
    path('admin/tickets/', views.admin_tickets, name='admin_tickets'),
    path('admin/tickets/update-status/<int:ticket_no>/', views.update_ticket_status, name='update_ticket_status'),
    path('support/tickets/admin/', views.admin_tickets, name='admin_tickets'),
    path('support/tickets/admin/update-status/<int:ticket_no>/', views.update_ticket_status, name='update_ticket_status'),
    path('health/', health_check, name='health_check'),
    path(
        'episodes/<str:custom_id>/analysis/',
        views.episode_analysis_view,
        name='episode_analysis'
    ),
    path('playlist/create/', views.playlist_create, name='playlist_create'),
    path('content/available/', AvailableContentView.as_view(), name='available_content'),
    path('content/available/programs/', views.available_programs, name='available_programs'),

    # path('content/available/update/', 
    #      AvailableContentView.as_view(action='update_episode'), 
    #      name='update_episode'),
    path('delete-episode/<str:episode_id>/', views.delete_episode, name='delete-episode'),
    path('delete-program/<str:program_id>/', views.delete_program, name='delete-program'),
    path('export-to-s3/<str:schedule_date>/', views.export_and_copy_to_s3, name='export_to_s3'),
    path('my_schedule/', views.my_schedule, name='my-schedule'),
    # path('env/', views.environment, name='environment_variables'),
    # path(
    #     'password_reset/',
    #     auth_views.PasswordResetView.as_view(
    #         template_name='registration/password_reset_form.html',
    #         email_template_name='registration/password_reset_email.html',
    #         subject_template_name='registration/password_reset_subject.txt',
    #         success_url=reverse_lazy('password_reset_done')
    #     ),
    #     name='password_reset'
    # ),
    
    # # Confirm reset link sent
    # path(
    #     'password_reset/done/',
    #     auth_views.PasswordResetDoneView.as_view(
    #         template_name='registration/password_reset_done.html'
    #     ),
    #     name='password_reset_done'
    # ),
    
    # # Link from the email to reset the password
    # path(
    #     'reset/<uidb64>/<token>/',
    #     auth_views.PasswordResetConfirmView.as_view(
    #         template_name='registration/password_reset_confirm.html',
    #         success_url='/reset/done/'
    #     ),
    #     name='password_reset_confirm'
    # ),
    
    # # Confirmation that the password was changed
    # path(
    #     'reset/done/',
    #     auth_views.PasswordResetCompleteView.as_view(
    #         template_name='registration/password_reset_complete.html'
    #     ),
    #     name='password_reset_complete'
    # ),

    path('test-email/', test_email, name='test_email'),

    path('accounts/login/', RedirectView.as_view(url='/creators/login_user', permanent=False), name='login'),
    
    re_path(r'^\.well-known/acme-challenge/(?P<token>[\w-]+)$', acme_challenge_view),

]


