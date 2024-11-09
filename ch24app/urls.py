from django.urls import path
from . import views

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
    path('upload_episode/<episode_id>/', views.upload_episode, name='upload_episode'),
    path('upload_success/', views.upload_success, name='upload_success'),
    path('upload_episode/<str:episode_id>/', views.upload_episode, name='upload_episode'),
    path('adobe_premiere/', views.adobe_premiere, name='adobe_premiere'),
    path('davinci_resolve/', views.davinci_resolve, name='davinci_resolve'),
    path('getting_started/', views.getting_started, name='getting_started'),
    path('episode/<str:episode_id>/media_info/', views.episode_media_info, name='episode_media_info'),

]


