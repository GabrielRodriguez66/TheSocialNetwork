from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path("friends/", views.MyFriendsView.as_view(), name="my_friends"),
    path('timeline/', views.timeline, name='timeline'),
    path('search/', views.search, name="search"),
    path(r"register/", views.register, name="register"),
    path("unfriend/<int:friend_pk>", views.unfriend, name="unfriend"),
    path("sunfriend/<int:friend_pk>", views.search_view_unfriend, name="search_unfriend"),
    path(r'asocia_usuario/', views.asocia_usuario, name='asocia_usuario'),
    path("login/", views.login_view, name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
]
