from urllib.parse import quote
from functools import wraps

from django.shortcuts import redirect
from django.urls import reverse


def login_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.session.get("user_id"):
            return redirect(f"{reverse('login')}?next={quote(request.get_full_path())}")
        return view(request, *args, **kwargs)

    return wrapped


def owner_id(request) -> str:
    return request.session["user_id"]


def safe_next(value):
    if value and value.startswith("/") and not value.startswith("//") and "\\" not in value:
        return value
    return reverse("home")
