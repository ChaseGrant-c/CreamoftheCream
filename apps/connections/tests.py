from datetime import timedelta

from django.test import Client, TestCase
from django.utils import timezone

from apps.connections.feeds import host_is_blocked, import_public_feed, validate_public_feed_url
from apps.connections.forms import ConnectionForm
from apps.connections.models import Connection, Post


class CreamTests(TestCase):
    def test_health(self):
        response = self.client.get("/healthz/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ok")

    def test_home_requires_sign_in(self):
        response = self.client.get("/")
        self.assertRedirects(response, "/login/?next=/")

    def test_demo_roster_shows_today_and_people(self):
        response = self.client.post("/login/", {"demo": "1"})
        self.assertRedirects(response, "/")
        home = self.client.get("/")
        self.assertContains(home, "Top of the day")
        self.assertContains(home, "Amira Shah")
        self.assertContains(home, "In rotation")
        people = self.client.get("/people/")
        self.assertContains(people, "Favorites")
        self.assertContains(people, "Jonah Ellison")
        person = Connection.objects.get(name="Amira Shah")
        detail = self.client.get(f"/people/{person.id}/")
        self.assertContains(detail, "activation rewrite")
        self.assertContains(detail, "https://example.com/amira")

    def test_another_account_cannot_open_a_person(self):
        self.client.post("/login/", {"demo": "1"})
        person = Connection.objects.get(name="Priya Raman")
        other = Client()
        session = other.session
        session["user_id"] = "22222222-2222-4222-8222-222222222222"
        session["email"] = "other@example.com"
        session.save()
        response = other.get(f"/people/{person.id}/")
        self.assertEqual(response.status_code, 404)

    def test_latest_label_when_nothing_was_posted_today(self):
        session = self.client.session
        session["user_id"] = "33333333-3333-4333-8333-333333333333"
        session["email"] = "solo@example.com"
        session.save()
        person = Connection.objects.create(
            owner_id=session["user_id"],
            name="Solo Reader",
            headline="Editor",
        )
        Post.objects.create(
            owner_id=session["user_id"],
            connection=person,
            body="An older note that should fall into Latest.",
            posted_at=timezone.now() - timedelta(days=3),
        )
        response = self.client.get("/")
        self.assertContains(response, "Nothing new today")
        self.assertContains(response, "An older note")

    def test_social_hosts_are_not_fetched(self):
        blocked = [
            "https://linkedin.com/in/a",
            "https://www.instagram.com/a",
            "https://m.facebook.com/a",
            "https://x.com/a",
            "https://twitter.com/a",
            "https://www.threads.net/@a",
            "https://tiktok.com/@a",
        ]
        for url in blocked:
            self.assertTrue(host_is_blocked(url), url)
        self.assertFalse(host_is_blocked("https://example.com/feed.xml"))
        self.assertIsNotNone(validate_public_feed_url("http://127.0.0.1/feed.xml"))
        self.assertIsNotNone(validate_public_feed_url("https://www.linkedin.com/in/someone"))

    def test_connection_form_rejects_a_social_feed_url(self):
        form = ConnectionForm(
            data={
                "name": "Pat",
                "headline": "",
                "bio": "",
                "notes": "",
                "email": "",
                "phone": "",
                "location": "",
                "avatar_url": "",
                "rss_url": "https://www.linkedin.com/in/pat",
                "link1_platform": "",
                "link1_url": "",
                "link2_platform": "",
                "link2_url": "",
                "link3_platform": "",
                "link3_url": "",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("rss_url", form.errors)

    def test_import_refuses_a_social_url_without_calling_it(self):
        person = Connection.objects.create(
            owner_id="44444444-4444-4444-8444-444444444444",
            name="Pat",
            rss_url="https://instagram.com/pat",
        )
        created, error = import_public_feed(person)
        self.assertEqual(created, 0)
        self.assertIn("open feed", error)

    def test_add_person_from_the_list(self):
        self.client.post("/login/", {"demo": "1"})
        response = self.client.post(
            "/people/new/",
            {
                "name": "Ada West",
                "headline": "Editor",
                "bio": "Reads the long pieces.",
                "notes": "",
                "email": "",
                "phone": "",
                "location": "Boulder",
                "avatar_url": "",
                "rss_url": "",
                "link1_platform": "website",
                "link1_url": "https://example.com/ada",
                "link2_platform": "",
                "link2_url": "",
                "link3_platform": "",
                "link3_url": "",
            },
        )
        person = Connection.objects.get(name="Ada West")
        self.assertRedirects(response, f"/people/{person.id}/")
        self.assertEqual(person.links.get().platform, "website")
