from django.contrib import admin
from django.urls import path
from . import views 
from django.conf.urls.static import static

urlpatterns = [
    path('', views.guestuser, name='guestuser'),
    path('index/', views.index, name='index'),
    path('landing/', views.landing_page, name='landing_page'),
    path('login/', views.user_login, name='user_login'),
    path('register/', views.register_page, name='register'),
    path('register_admin/', views.register_admin, name='register_admin'),
    path('register_member/', views.register_member, name='register_member'),
    path('logout/', views.log_out, name='log_out'),
    path("member/<str:username>/", views.member_details, name="member_details"),
    path("member/<str:username>/delete/", views.delete_member, name="delete_member"),
    path("create/", views.create_album, name="create_album"),
    path("album/<int:album_id>/delete/", views.delete_album, name="delete_album"),
    path('album/<int:album_id>/', views.album_detail, name='album_detail'),
    path("albums/", views.album_list, name="album_list"),
    path("<int:album_id>/edit/", views.album_edit, name="album_edit"),
    path("memories/", views.memory_list, name="memory_list"),
    path("delete_memory/<int:memory_id>/", views.memory_delete, name="memory_delete"),
    path('memories_details/', views.memory_detail, name='memory_detail'),
    path('album/<int:album_id>/add-photo/', views.add_photo_to_album, name='add_photo_to_album'),
    path("memories/<int:memory_id>/add-to-album/", views.add_memory_to_album, name="add_memory_to_album"),

]