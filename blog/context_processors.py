from django.core.cache import cache

from .models import Publication


def publications(request):
    pubs = cache.get("all_publications")
    if pubs is None:
        pubs = list(Publication.objects.all())
        cache.set("all_publications", pubs, 300)  # Cache 5 minutes
    return {"publications": pubs}
