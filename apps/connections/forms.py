from urllib.parse import urlparse

from django import forms

from apps.connections.feeds import BLOCKED_MESSAGE, host_is_blocked
from apps.connections.models import PLATFORM_CHOICES, Connection, Post

LINK_PLATFORM_CHOICES = [("", "Platform")] + PLATFORM_CHOICES


def _web_url(url):
    if not url:
        return url
    scheme = urlparse(url).scheme
    if scheme not in {"http", "https"}:
        raise forms.ValidationError("Use a link that starts with http or https.")
    return url


class ConnectionForm(forms.ModelForm):
    link1_platform = forms.ChoiceField(choices=LINK_PLATFORM_CHOICES, required=False, label="Platform")
    link1_url = forms.URLField(required=False, label="Profile URL", assume_scheme="https")
    link2_platform = forms.ChoiceField(choices=LINK_PLATFORM_CHOICES, required=False, label="Platform")
    link2_url = forms.URLField(required=False, label="Profile URL", assume_scheme="https")
    link3_platform = forms.ChoiceField(choices=LINK_PLATFORM_CHOICES, required=False, label="Platform")
    link3_url = forms.URLField(required=False, label="Profile URL", assume_scheme="https")

    class Meta:
        model = Connection
        fields = [
            "name",
            "headline",
            "bio",
            "notes",
            "email",
            "phone",
            "location",
            "avatar_url",
            "rss_url",
            "is_favorite",
        ]
        labels = {
            "headline": "Short description",
            "bio": "About",
            "notes": "Private notes",
            "avatar_url": "Profile image URL",
            "rss_url": "Public RSS or Atom URL",
            "is_favorite": "Favorite",
        }
        help_texts = {
            "notes": "Only you see this.",
            "rss_url": "A public blog or newsletter feed. LinkedIn, Instagram, and Facebook stay as links.",
        }
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "name": "Name",
            "headline": "Short line under their name",
            "email": "Email",
            "phone": "Phone",
            "location": "City",
            "avatar_url": "https://",
            "rss_url": "https://example.com/feed.xml",
        }
        for field_name, text in placeholders.items():
            self.fields[field_name].widget.attrs["placeholder"] = text
            self.fields[field_name].widget.attrs["autocomplete"] = "off"
        for slot in (1, 2, 3):
            self.fields[f"link{slot}_url"].widget.attrs.update(
                {"placeholder": "https://", "autocomplete": "off"}
            )
        if self.instance.pk:
            links = list(self.instance.links.all()[:3])
            for slot, link in enumerate(links, start=1):
                self.fields[f"link{slot}_platform"].initial = link.platform
                self.fields[f"link{slot}_url"].initial = link.url

    def link_slots(self):
        return [(self[f"link{slot}_platform"], self[f"link{slot}_url"]) for slot in (1, 2, 3)]

    def clean_name(self):
        return " ".join(self.cleaned_data["name"].split())

    def clean_avatar_url(self):
        return _web_url(self.cleaned_data.get("avatar_url", ""))

    def clean_rss_url(self):
        url = _web_url(self.cleaned_data.get("rss_url", ""))
        if url and host_is_blocked(url):
            raise forms.ValidationError(BLOCKED_MESSAGE)
        return url

    def clean(self):
        cleaned = super().clean()
        for slot in (1, 2, 3):
            url = cleaned.get(f"link{slot}_url")
            platform = cleaned.get(f"link{slot}_platform")
            if url and not platform:
                self.add_error(f"link{slot}_platform", "Choose a platform for this link.")
            if url:
                try:
                    _web_url(url)
                except forms.ValidationError as exc:
                    self.add_error(f"link{slot}_url", exc)
        return cleaned


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "body", "platform", "external_url", "posted_at", "is_highlight"]
        labels = {
            "body": "Post",
            "external_url": "Link to the original",
            "posted_at": "Posted",
            "is_highlight": "Pin to today's cream",
        }
        widgets = {
            "body": forms.Textarea(attrs={"rows": 6, "placeholder": "Paste or write the post"}),
            "title": forms.TextInput(attrs={"placeholder": "Optional title"}),
            "external_url": forms.URLInput(attrs={"placeholder": "https://"}),
            "posted_at": forms.DateTimeInput(
                format="%Y-%m-%dT%H:%M",
                attrs={"type": "datetime-local"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["posted_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%dT%H:%M:%S"]
        self.fields["title"].required = False
        self.fields["external_url"].required = False

    def clean_external_url(self):
        return _web_url(self.cleaned_data.get("external_url", ""))
