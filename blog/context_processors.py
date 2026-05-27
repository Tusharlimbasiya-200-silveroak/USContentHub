from django.conf import settings
from django.core.cache import cache

from .models import Publication


def publications(request):
    pubs = cache.get("all_publications")
    if pubs is None:
        try:
            pubs = list(Publication.objects.all())
        except Exception:
            pubs = []
        cache.set("all_publications", pubs, 300)
    return {
        "publications": pubs,
        "site_url": getattr(settings, "SITE_URL", "").rstrip("/"),
    }
