from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from apps.accounts.decorators import login_required, owner_id
from apps.connections.feeds import import_public_feed
from apps.connections.forms import ConnectionForm, PostForm
from apps.connections.models import Connection, Post
from apps.connections.roster import alphabet_for, grouped_people, popular_connections, top_posts


def _owned(request, connection_id):
    return get_object_or_404(Connection.objects.for_owner(owner_id(request)), pk=connection_id)


def _save_links(person, form):
    person.links.all().delete()
    for slot in (1, 2, 3):
        url = form.cleaned_data.get(f"link{slot}_url")
        platform = form.cleaned_data.get(f"link{slot}_platform") or "other"
        if url:
            person.links.create(platform=platform, url=url)


@login_required
def home(request):
    oid = owner_id(request)
    posts, showing_latest = top_posts(oid)
    return render(
        request,
        "connections/home.html",
        {
            "posts": posts,
            "showing_latest": showing_latest,
            "popular": popular_connections(oid),
            "today": timezone.localtime(),
        },
    )


@login_required
def people(request):
    query = request.GET.get("q", "").strip()
    favorites, groups = grouped_people(owner_id(request), query)
    return render(
        request,
        "connections/people.html",
        {
            "query": query,
            "favorites": favorites,
            "groups": groups,
            "alphabet": alphabet_for(groups),
        },
    )


@login_required
def connection_detail(request, connection_id):
    person = get_object_or_404(
        Connection.objects.for_owner(owner_id(request)).prefetch_related("links"),
        pk=connection_id,
    )
    posts = person.posts.all()[:40]
    return render(
        request,
        "connections/detail.html",
        {"person": person, "posts": posts},
    )


@login_required
@require_http_methods(["GET", "POST"])
def connection_create(request):
    form = ConnectionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        person = form.save(commit=False)
        person.owner_id = owner_id(request)
        person.save()
        _save_links(person, form)
        messages.success(request, f"Added {person.name}.")
        return redirect("connection-detail", connection_id=person.id)
    return render(
        request,
        "connections/connection_form.html",
        {"form": form, "heading": "Add a person", "person": None},
    )


@login_required
@require_http_methods(["GET", "POST"])
def connection_edit(request, connection_id):
    person = get_object_or_404(
        Connection.objects.for_owner(owner_id(request)).prefetch_related("links"),
        pk=connection_id,
    )
    form = ConnectionForm(request.POST or None, instance=person)
    if request.method == "POST" and form.is_valid():
        person = form.save(commit=False)
        person.owner_id = owner_id(request)
        person.save()
        _save_links(person, form)
        messages.success(request, f"Updated {person.name}.")
        return redirect("connection-detail", connection_id=person.id)
    return render(
        request,
        "connections/connection_form.html",
        {"form": form, "heading": "Edit", "person": person},
    )


@login_required
@require_POST
def connection_delete(request, connection_id):
    person = _owned(request, connection_id)
    name = person.name
    person.delete()
    messages.success(request, f"Removed {name}.")
    return redirect("people")


@login_required
@require_POST
def toggle_favorite(request, connection_id):
    person = _owned(request, connection_id)
    person.is_favorite = not person.is_favorite
    person.save(update_fields=["is_favorite", "updated_at"])
    return redirect("connection-detail", connection_id=person.id)


@login_required
@require_http_methods(["GET", "POST"])
def post_create(request, connection_id):
    person = _owned(request, connection_id)
    initial = {"posted_at": timezone.localtime().strftime("%Y-%m-%dT%H:%M")}
    first_link = person.links.first()
    if first_link:
        initial["platform"] = first_link.platform
    form = PostForm(request.POST or None, initial=None if request.method == "POST" else initial)
    if request.method == "POST" and form.is_valid():
        post = form.save(commit=False)
        post.owner_id = owner_id(request)
        post.connection = person
        post.source = Post.MANUAL
        post.save()
        messages.success(request, "Saved the post.")
        return redirect("connection-detail", connection_id=person.id)
    return render(
        request,
        "connections/post_form.html",
        {"form": form, "person": person},
    )


@login_required
@require_POST
def refresh_feed(request, connection_id):
    person = _owned(request, connection_id)
    if not person.rss_url:
        messages.error(request, "Add a public feed URL on the edit page first.")
        return redirect("connection-detail", connection_id=person.id)
    created, error = import_public_feed(person)
    if error:
        messages.error(request, error)
    elif created == 0:
        messages.info(request, "No new posts in that feed.")
    else:
        messages.success(request, f"Saved {created} new posts.")
    return redirect("connection-detail", connection_id=person.id)
