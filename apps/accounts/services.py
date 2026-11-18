import logging

from django.conf import settings

logger = logging.getLogger(__name__)


class AuthError(Exception):
    pass


class AuthNotConfigured(AuthError):
    pass


class EmailConfirmationRequired(AuthError):
    pass


def _client():
    if not settings.SUPABASE_URL or not settings.SUPABASE_ANON_KEY:
        raise AuthNotConfigured("Supabase is not configured.")
    try:
        from supabase import create_client
    except ImportError as exc:
        raise AuthNotConfigured("The Supabase library is not installed.") from exc
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def _session_from(response, fallback_email):
    user = getattr(response, "user", None)
    session = getattr(response, "session", None)
    if user is None:
        raise AuthError("Supabase did not return an account.")
    if session is None:
        raise EmailConfirmationRequired()
    return {"user_id": str(user.id), "email": user.email or fallback_email}


def sign_in(email, password):
    client = _client()
    try:
        response = client.auth.sign_in_with_password({"email": email, "password": password})
    except Exception as exc:
        logger.warning("Supabase sign-in failed: %s", exc.__class__.__name__)
        raise AuthError("Email or password did not match.") from exc
    return _session_from(response, email)


def sign_up(email, password):
    client = _client()
    try:
        response = client.auth.sign_up({"email": email, "password": password})
    except Exception as exc:
        logger.warning("Supabase sign-up failed: %s", exc.__class__.__name__)
        raise AuthError("Could not create that account. If you already signed up, try signing in.") from exc
    return _session_from(response, email)
