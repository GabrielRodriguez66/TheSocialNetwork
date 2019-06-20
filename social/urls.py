from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path("chat/<int:friend_pk>/<str:view>", views.chat_manager, name="chat"),
    path("friends/", views.friends_view, name="friends"),
    path('timeline/', views.timeline, name='timeline'),
    path('search/', views.search, name="search"),
    path(r"register/", views.register, name="register"),
    path("unfriend/<int:friend_pk>/<str:view>", views.unfriend, name="unfriend"),
    path(r'asocia_usuario/', views.asocia_usuario, name='asocia_usuario'),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("profile/", views.profile, name="profile"),
    path("profile/picture", views.profile_pic, name="profile_pic"),
    path("profile/delete", views.delete_pic, name="delete_pic"),
]
