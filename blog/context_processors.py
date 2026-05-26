from .models import Publication


def publications(request):
    return {"publications": Publication.objects.all()}
