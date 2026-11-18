from django.contrib import admin

from apps.connections.models import Connection, Post, SocialLink


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ("name", "owner_id", "is_favorite", "location", "updated_at")
    search_fields = ("name", "email", "headline")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("connection", "platform", "url")


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("connection", "platform", "posted_at", "is_highlight", "source")
    list_filter = ("platform", "source", "is_highlight")
