from django.conf import settings


def session_user(request):
    return {
        "current_email": request.session.get("email", ""),
        "demo_session": bool(request.session.get("demo_mode")),
        "signed_in": bool(request.session.get("user_id")),
        "demo_available": settings.DEMO_MODE,
        "supabase_configured": settings.SUPABASE_CONFIGURED,
    }
