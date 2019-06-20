from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path("chat/<int:friend_pk>/<str:view>", views.chat_manager, name="chat"),
    path("friends/", views.friends_view, name="friends"),
    path('timeline/', views.timeline, name='timeline'),
    path('search/', views.search, name="search"),
    path(r"register/", views.register, name="register"),
    path("friend/<int:friend_pk>", views.friend_request, name="friend_request"),
    path("respond/<int:request_pk>/<int:accepted>", views.respond_request, name="respond_request"),
    path("unfriend/<int:friend_pk>/<str:view>", views.unfriend, name="unfriend"),
    path(r'asocia_usuario/', views.asocia_usuario, name='asocia_usuario'),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
]
