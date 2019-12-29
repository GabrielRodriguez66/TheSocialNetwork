from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path('timeline/', views.timeline, name='timeline'),
    path('search/', views.search, name="search"),
    path("friends/", views.friends_view, name="friends"),
    path("chats/", views.chats_manager, name="create_or_get_chat"),
    path("post_chat_message/<int:friend_pk>/<int:chat_pk>/", views.post_chat_message, name="post_chat_message"),
    path("friend/<int:friend_pk>", views.friend_request, name="friend_request"),
    path("friend/<str:friend_usuario_first_name>/profile", views.friend_prof, name='friend_profile'),
    path("respond/<int:request_pk>/<int:accepted>", views.respond_request, name="respond_request"),
    path("unfriend/<int:friend_pk>/<str:view>", views.unfriend, name="unfriend"),
    path('asocia_usuario/', views.asocia_usuario, name='asocia_usuario'),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("profile/", views.profile, name="profile"),
    path("profile/picture", views.profile_pic, name="profile_pic"),
    path("profile/delete-pic", views.delete_pic, name="delete_pic"),
    path('profile/delete', views.delete_prof, name="delete_prof")

]
