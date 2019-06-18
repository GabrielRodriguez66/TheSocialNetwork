from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path("friends/", views.MyFriendsView.as_view(), name="my_friends"),
    path(r"register/", views.register, name="register"),
    path("unfriend/<int:friend_pk>", views.unfriend, name="unfriend"),
    path(r'asocia_usuario/', views.asocia_usuario, name='asocia_usuario'),
]
