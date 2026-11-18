"""Import posts from a public RSS or Atom URL.

Profile links are stored as links. This module does not log in to LinkedIn,
Instagram, Facebook, or other social sites, and it does not collect their feeds.
"""

import ipaddress
import logging
import socket
import urllib.request
from datetime import datetime, timezone as dt_timezone
from html import unescape
from urllib.parse import urlparse

import feedparser
from django.utils import timezone
from django.utils.html import strip_tags

from apps.connections.models import Post

logger = logging.getLogger(__name__)

BLOCKED_HOSTS = (
    "linkedin.com",
    "instagram.com",
    "facebook.com",
    "fb.com",
    "fb.me",
    "x.com",
    "twitter.com",
    "threads.net",
    "tiktok.com",
    "t.co",
)
USER_AGENT = "CreamOfTheCream/0.1 (personal feed reader)"
BLOCKED_MESSAGE = (
    "That site does not offer an open feed. Save the post by hand, and keep the profile as a link."
)


class FeedRejected(Exception):
    pass


def host_is_blocked(url):
    host = (urlparse(url).hostname or "").lower().removeprefix("www.")
    return any(host == blocked or host.endswith("." + blocked) for blocked in BLOCKED_HOSTS)


def _host_is_public(hostname):
    hostname = hostname.strip(".").lower()
    if hostname in {"localhost", "localhost.localdomain"}:
        return False
    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        address = None
    if address is not None:
        return _ip_is_public(address)
    try:
        infos = socket.getaddrinfo(hostname, None)
    except socket.gaierror:
        return False
    addresses = []
    for info in infos:
        try:
            addresses.append(ipaddress.ip_address(info[4][0]))
        except ValueError:
            return False
    return bool(addresses) and all(_ip_is_public(address) for address in addresses)


def _ip_is_public(address):
    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_reserved
        or address.is_multicast
        or address.is_unspecified
    )


def validate_public_feed_url(url):
    parsed = urlparse((url or "").strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return "Feed URL must start with http or https."
    if host_is_blocked(url):
        return BLOCKED_MESSAGE
    if not _host_is_public(parsed.hostname):
        return "That feed address can't be reached from here."
    return None


class _GuardRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        error = validate_public_feed_url(newurl)
        if error:
            raise FeedRejected(error)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _posted_at(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        try:
            return datetime(*parsed[:6], tzinfo=dt_timezone.utc)
        except (TypeError, ValueError):
            pass
    return timezone.now()


def _text(value, limit):
    cleaned = unescape(strip_tags(value or ""))
    cleaned = " ".join(cleaned.split())
    return cleaned[:limit].strip()


def import_public_feed(connection, limit=15):
    url = (connection.rss_url or "").strip()
    error = validate_public_feed_url(url)
    if error:
        return 0, error
    opener = urllib.request.build_opener(_GuardRedirect)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with opener.open(request, timeout=8) as response:
            payload = response.read(1_000_000)
    except FeedRejected as exc:
        return 0, str(exc)
    except Exception:
        logger.info("Feed read failed for %s", connection.id)
        return 0, "Couldn't read that feed."

    parsed = feedparser.parse(payload)
    entries = list(getattr(parsed, "entries", []) or [])
    if not entries:
        return 0, "That URL did not return any feed entries."

    created = 0
    for entry in entries[:limit]:
        link = (entry.get("link") or "").strip()
        if link and connection.posts.filter(external_url=link).exists():
            continue
        title = _text(entry.get("title"), 200)
        body = _text(entry.get("summary") or entry.get("description") or title, 4000)
        if not body:
            continue
        if link and host_is_blocked(link):
            link = ""
        Post.objects.create(
            owner_id=connection.owner_id,
            connection=connection,
            platform="website",
            title=title if title != body else "",
            body=body,
            external_url=link if link.startswith(("http://", "https://")) else "",
            posted_at=_posted_at(entry),
            source=Post.RSS,
        )
        created += 1
    return created, None
