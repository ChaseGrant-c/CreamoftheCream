import string
from collections import defaultdict
from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from apps.connections.models import Connection, Post


def top_posts(owner_id):
    start = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    posts = list(
        Post.objects.for_owner(owner_id)
        .filter(posted_at__gte=start)
        .select_related("connection")
        .order_by("-is_highlight", "-posted_at")[:8]
    )
    showing_latest = False
    if not posts:
        showing_latest = True
        posts = list(
            Post.objects.for_owner(owner_id).select_related("connection").order_by("-posted_at")[:8]
        )
    return posts, showing_latest


def popular_connections(owner_id):
    week_ago = timezone.now() - timedelta(days=7)
    return list(
        Connection.objects.for_owner(owner_id)
        .annotate(recent_posts=Count("posts", filter=Q(posts__posted_at__gte=week_ago)))
        .prefetch_related("links")
        .order_by("-is_favorite", "-recent_posts", "name")[:8]
    )


def grouped_people(owner_id, query=""):
    people = Connection.objects.for_owner(owner_id).prefetch_related("links")
    if query:
        people = people.filter(
            Q(name__icontains=query)
            | Q(headline__icontains=query)
            | Q(email__icontains=query)
            | Q(location__icontains=query)
        )
    favorites = []
    buckets = defaultdict(list)
    for person in people.order_by("name"):
        letter = person.name.strip()[:1].upper()
        if not letter.isalpha():
            letter = "#"
        buckets[letter].append(person)
        if person.is_favorite and not query:
            favorites.append(person)
    ordered = sorted(buckets, key=lambda letter: (letter == "#", letter))
    groups = [
        {
            "letter": letter,
            "anchor": "hash" if letter == "#" else letter,
            "people": buckets[letter],
        }
        for letter in ordered
    ]
    return favorites, groups


def alphabet_for(groups):
    present = {group["letter"] for group in groups}
    letters = list(string.ascii_uppercase)
    if "#" in present:
        letters.append("#")
    return [
        {
            "letter": letter,
            "anchor": "hash" if letter == "#" else letter,
            "present": letter in present,
        }
        for letter in letters
    ]
