from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

admin.site.site_header = "Cream of the Cream"
admin.site.site_title = "Cream of the Cream"


def healthz(request):
    return HttpResponse("ok")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("healthz/", healthz, name="healthz"),
    path("", include("apps.accounts.urls")),
    path("", include("apps.connections.urls")),
]
