import logging

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Article

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Article)
def _capture_old_status(sender, instance, **kwargs):
    """Store the previous status before save so post_save can detect the draft→published transition."""
    if instance.pk:
        instance._old_status = (
            Article.objects.filter(pk=instance.pk)
            .values_list("status", flat=True)
            .first()
        )
    else:
        instance._old_status = None


@receiver(post_save, sender=Article)
def _auto_pin_on_publish(sender, instance, created, **kwargs):
    """Fire a Pinterest pin when an article transitions to published for the first time."""
    old_status = getattr(instance, "_old_status", None)
    is_newly_published = instance.status == "published" and old_status != "published"

    if not is_newly_published:
        return

    try:
        from .pinterest import create_pin
        site_url = getattr(settings, "SITE_URL", "https://us-content-hub.vercel.app").rstrip("/")
        create_pin(instance, site_url)
    except Exception:
        logger.exception(
            "Pinterest: unexpected error while pinning article '%s'", instance.slug
        )
