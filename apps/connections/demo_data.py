from datetime import timedelta
from uuid import UUID

from django.utils import timezone

from apps.connections.models import Connection, Post, SocialLink

DEMO_OWNER_ID = UUID("11111111-1111-4111-8111-111111111111")


def _when(spec, now):
    if "days_ago" in spec:
        return now - timedelta(days=spec["days_ago"])
    return now - timedelta(hours=spec.get("hours_ago", 0))


def seed_demo(owner_id=DEMO_OWNER_ID):
    if Connection.objects.for_owner(owner_id).exists():
        return owner_id
    now = timezone.now()
    roster = [
        {
            "name": "Amira Shah",
            "headline": "Product lead",
            "location": "Denver",
            "email": "amira@example.com",
            "phone": "303-555-0148",
            "bio": "Ships the quiet parts of a product: onboarding, empty states, the sentence on the button.",
            "notes": "Ask about the activation rewrite before the next coffee.",
            "is_favorite": True,
            "links": [("linkedin", "https://example.com/amira")],
            "posts": [
                {
                    "platform": "linkedin",
                    "body": "Shipped the onboarding rewrite. Activation is up, support tickets are not. The unglamorous version of a good week.",
                    "external_url": "https://example.com/amira/onboarding",
                    "hours_ago": 1,
                    "is_highlight": True,
                },
                {
                    "platform": "linkedin",
                    "title": "Notes from the rewrite",
                    "body": "We cut the signup form from nine fields to four. The rest can wait until someone actually wants them.",
                    "days_ago": 4,
                },
            ],
        },
        {
            "name": "Jonah Ellison",
            "headline": "Photographer",
            "location": "Santa Fe",
            "bio": "Makes pictures in the hour before other people are awake.",
            "links": [("instagram", "https://example.com/jonah")],
            "posts": [
                {
                    "platform": "instagram",
                    "body": "Dawn loop at the track. No playlist, just the count.",
                    "external_url": "https://example.com/jonah/dawn",
                    "hours_ago": 3,
                }
            ],
        },
        {
            "name": "Priya Raman",
            "headline": "Writes a Tuesday letter",
            "location": "Chicago",
            "bio": "A newsletter about attention, archives, and leaving the group chat.",
            "links": [("website", "https://example.com/priya")],
            "posts": [
                {
                    "platform": "website",
                    "title": "Before noon",
                    "body": "I stopped reading comment sections before noon. The morning got its voice back.",
                    "external_url": "https://example.com/priya/noon",
                    "hours_ago": 5,
                    "is_highlight": True,
                }
            ],
        },
        {
            "name": "Leo Park",
            "headline": "Community manager",
            "location": "Oakland",
            "bio": "Keeps a neighborhood group kind without making it dull.",
            "links": [("facebook", "https://example.com/leo")],
            "posts": [
                {
                    "platform": "facebook",
                    "body": "The block party list is up. Bring a chair if you have one.",
                    "days_ago": 3,
                }
            ],
        },
        {
            "name": "Camila Ortiz",
            "headline": "Brand studio",
            "location": "Austin",
            "bio": "Designs identities that still sound like the founder.",
            "notes": "Introduced by Priya. Prefers a voice note to a deck.",
            "is_favorite": True,
            "links": [("x", "https://example.com/camila")],
            "posts": [
                {
                    "platform": "x",
                    "body": "A logo is the least interesting part of a rebrand. The words did the work.",
                    "hours_ago": 2,
                }
            ],
        },
        {
            "name": "Noah Abebe",
            "headline": "Coach",
            "location": "Boulder",
            "bio": "Trains runners who want one goal, not twelve.",
            "links": [("threads", "https://example.com/noah")],
            "posts": [],
        },
        {
            "name": "Beatrice Okonkwo",
            "headline": "Cook and teacher",
            "location": "Houston",
            "bio": "Teaches weeknight food that does not require a special pan.",
            "links": [("tiktok", "https://example.com/beatrice")],
            "posts": [],
        },
        {
            "name": "Mateo Alvarez",
            "headline": "Independent journalist",
            "location": "El Paso",
            "bio": "Reports on water, work, and the bus that actually came.",
            "links": [("website", "https://example.com/mateo")],
            "posts": [
                {
                    "platform": "website",
                    "title": "The 6:10",
                    "body": "The 6:10 bus has been on time three mornings in a row. People are treating it like news, because it is.",
                    "days_ago": 2,
                }
            ],
        },
    ]
    for item in roster:
        links = item.pop("links")
        posts = item.pop("posts")
        person = Connection.objects.create(owner_id=owner_id, **item)
        for platform, url in links:
            SocialLink.objects.create(connection=person, platform=platform, url=url)
        for spec in posts:
            Post.objects.create(
                owner_id=owner_id,
                connection=person,
                platform=spec["platform"],
                title=spec.get("title", ""),
                body=spec["body"],
                external_url=spec.get("external_url", ""),
                posted_at=_when(spec, now),
                is_highlight=spec.get("is_highlight", False),
                source=Post.MANUAL,
            )
    return owner_id
