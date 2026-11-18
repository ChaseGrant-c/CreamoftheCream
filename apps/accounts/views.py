from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from apps.accounts.decorators import safe_next
from apps.accounts.forms import LoginForm, SignupForm
from apps.accounts.services import AuthError, AuthNotConfigured, EmailConfirmationRequired, sign_in, sign_up
from apps.connections.demo_data import seed_demo


def _store_session(request, session, demo=False):
    request.session["user_id"] = session["user_id"]
    request.session["email"] = session["email"]
    request.session["demo_mode"] = demo


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.session.get("user_id"):
        return redirect("home")
    if request.method == "POST" and request.POST.get("demo") == "1":
        if not settings.DEMO_MODE:
            messages.error(request, "The sample roster is only available before Supabase is connected.")
            return redirect("login")
        user_id = seed_demo()
        _store_session(request, {"user_id": str(user_id), "email": "demo@creamofthecream.local"}, demo=True)
        return redirect(safe_next(request.POST.get("next") or request.GET.get("next")))

    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            session = sign_in(form.cleaned_data["email"], form.cleaned_data["password"])
        except EmailConfirmationRequired:
            messages.info(request, "Confirm the email from Supabase, then sign in.")
        except AuthNotConfigured:
            messages.error(request, "Supabase is not configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY.")
        except AuthError as exc:
            messages.error(request, str(exc))
        else:
            _store_session(request, session)
            return redirect(safe_next(request.POST.get("next") or request.GET.get("next")))
    return render(request, "accounts/login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.session.get("user_id"):
        return redirect("home")
    form = SignupForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            session = sign_up(form.cleaned_data["email"], form.cleaned_data["password"])
        except EmailConfirmationRequired:
            messages.info(request, "Check your email for a confirmation from Supabase, then sign in.")
            return redirect("login")
        except AuthNotConfigured:
            messages.error(request, "Supabase is not configured yet. Add SUPABASE_URL and SUPABASE_ANON_KEY.")
        except AuthError as exc:
            messages.error(request, str(exc))
        else:
            _store_session(request, session)
            messages.success(request, "Account created.")
            return redirect("home")
    return render(request, "accounts/signup.html", {"form": form})


@require_POST
def logout_view(request):
    request.session.flush()
    return redirect("login")
