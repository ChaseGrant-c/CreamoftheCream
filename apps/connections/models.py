import uuid

from django.db import models


PLATFORM_CHOICES = [
    ("linkedin", "LinkedIn"),
    ("instagram", "Instagram"),
    ("facebook", "Facebook"),
    ("x", "X"),
    ("threads", "Threads"),
    ("tiktok", "TikTok"),
    ("website", "Website"),
    ("other", "Other"),
]


class OwnedQuerySet(models.QuerySet):
    def for_owner(self, owner_id):
        return self.filter(owner_id=owner_id)


class OwnedManager(models.Manager.from_queryset(OwnedQuerySet)):
    pass


class Connection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=120)
    headline = models.CharField(max_length=180, blank=True)
    bio = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    avatar_url = models.URLField(blank=True)
    rss_url = models.URLField(blank=True)
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = OwnedManager()

    class Meta:
        db_table = "focus_people"
        ordering = ["name"]
        indexes = [models.Index(fields=["owner_id", "name"])]

    def __str__(self):
        return self.name


class SocialLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    connection = models.ForeignKey(Connection, related_name="links", on_delete=models.CASCADE)
    platform = models.CharField(max_length=32, choices=PLATFORM_CHOICES)
    url = models.URLField()

    class Meta:
        db_table = "focus_links"
        ordering = ["platform", "url"]

    def __str__(self):
        return f"{self.get_platform_display()} for {self.connection.name}"


class Post(models.Model):
    MANUAL = "manual"
    RSS = "rss"
    SOURCE_CHOICES = [
        (MANUAL, "Saved by hand"),
        (RSS, "Public feed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner_id = models.UUIDField(db_index=True)
    connection = models.ForeignKey(Connection, related_name="posts", on_delete=models.CASCADE)
    platform = models.CharField(max_length=32, choices=PLATFORM_CHOICES, default="other")
    title = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    external_url = models.URLField(blank=True)
    posted_at = models.DateTimeField()
    captured_at = models.DateTimeField(auto_now_add=True)
    is_highlight = models.BooleanField(default=False)
    source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=MANUAL)

    objects = OwnedManager()

    class Meta:
        db_table = "focus_posts"
        ordering = ["-posted_at"]
        indexes = [models.Index(fields=["owner_id", "posted_at"])]

    def __str__(self):
        return self.title or self.body[:48]
