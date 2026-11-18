from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("people/", views.people, name="people"),
    path("people/new/", views.connection_create, name="connection-create"),
    path("people/<uuid:connection_id>/", views.connection_detail, name="connection-detail"),
    path("people/<uuid:connection_id>/edit/", views.connection_edit, name="connection-edit"),
    path("people/<uuid:connection_id>/delete/", views.connection_delete, name="connection-delete"),
    path("people/<uuid:connection_id>/favorite/", views.toggle_favorite, name="toggle-favorite"),
    path("people/<uuid:connection_id>/posts/new/", views.post_create, name="post-create"),
    path("people/<uuid:connection_id>/feed/", views.refresh_feed, name="refresh-feed"),
]
