from . import views
from django.urls import path

urlpatterns = [
    path("",views.index, name="index"),
    path("login",views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("category/<str:tab>", views.tabs, name="tabs"),
    path("rooms/<int:id>", views.rooms, name="rooms"),
    path("settings/<int:id>", views.settings, name="settings"),
    path('group/<int:group_id>/add_member/', views.add_member, name='add_member'),
    path('group/<int:group_id>/remove_member/', views.remove_member, name='remove_member'),

    path("room", views.create_room, name="create_room"),
    
]
