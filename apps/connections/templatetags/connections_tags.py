from django import template

register = template.Library()


@register.filter
def initials(name):
    parts = [part for part in (name or "").split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


@register.filter
def excerpt(text, limit=220):
    words = " ".join((text or "").split())
    limit = int(limit)
    if len(words) <= limit:
        return words
    clipped = words[:limit].rsplit(" ", 1)[0]
    return f"{clipped}…"
