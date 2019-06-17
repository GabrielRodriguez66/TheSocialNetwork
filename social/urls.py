from django.urls import path

from . import views

app_name = 'social'
urlpatterns = [
    path("friends/", views.MyFriendsView.as_view(), name="my_friends"),
    path("unfriend/<int:friend_pk>", views.unfriend, name="unfriend"),
]
