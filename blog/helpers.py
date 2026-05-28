"""
blog/helpers.py — shared utilities for the blog app.

Imported by views.py (and any management commands) so that views.py
stays focused on HTTP request/response logic only.

Sections:
  1. IP extraction
  2. Rate limiting
  3. Cache helper
  4. Email delivery
"""

import logging

from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)


# ── 1. IP extraction ──────────────────────────────────────────────────────────

def get_client_ip(request) -> str:
    """
    Return the real client IP, honouring X-Forwarded-For when present
    (e.g. behind Vercel's edge network or a reverse proxy).
    """
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


# ── 2. Rate limiting ──────────────────────────────────────────────────────────

def check_rate_limit(key: str, max_count: int) -> bool:
    """
    Return True if the caller has exceeded max_count actions for this key.
    Call bump_rate_counter() after a successful action to increment the tally.
    """
    return cache.get(key, 0) >= max_count


def bump_rate_counter(key: str, window: int) -> None:
    """
    Increment the rate-limit counter for *key* and (re-)set its TTL to
    *window* seconds.  Safe to call even if the key has expired.
    """
    cache.set(key, cache.get(key, 0) + 1, window)


# ── 3. Cache helper ───────────────────────────────────────────────────────────

def cache_or_set(key: str, timeout: int, getter):
    """
    Return the cached value for *key*.  If the key is missing, call
    *getter()* to produce the value, store it for *timeout* seconds, and
    return it.

    Usage::

        tags = cache_or_set(
            "popular_tags_15", 300,
            lambda: list(Tag.objects.annotate(count=Count("articles"))
                         .order_by("-count")[:15])
        )
    """
    value = cache.get(key)
    if value is None:
        value = getter()
        cache.set(key, value, timeout)
    return value


# ── 4. Email delivery ─────────────────────────────────────────────────────────

def send_newsletter_welcome(email: str) -> bool:
    """
    Send a branded HTML+text welcome email to a new newsletter subscriber.

    Returns True on success, False on any SMTP failure.
    Never raises — email failure must not break the subscription flow.
    """
    try:
        text_body = render_to_string("blog/emails/newsletter_welcome.txt")
        html_body = render_to_string("blog/emails/newsletter_welcome.html")
        msg = EmailMultiAlternatives(
            subject="Welcome to USA Content Hub Newsletter!",
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.send(fail_silently=False)
        logger.info("Newsletter welcome sent to %s", email)
        return True
    except Exception as exc:
        logger.error("SMTP ERROR — newsletter welcome failed for %s: %s", email, exc)
        return False


def send_contact_emails(
    name: str, email: str, subject: str, message: str, ip: str
) -> bool:
    """
    Send two emails for a contact form submission:
      1. Admin notification → settings.CONTACT_EMAIL  (reply-to = sender)
      2. Confirmation        → sender's email address  (HTML + plain text)

    Returns True if both emails sent, False on any SMTP failure.
    Never raises — email failure is logged but does not surface to the user.
    """
    try:
        # 1. Admin notification (plain text)
        admin_body = render_to_string("blog/emails/contact_notification.txt", {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
            "ip": ip,
        })
        msg_admin = EmailMultiAlternatives(
            subject=f"[Contact] {subject} — from {name}",
            body=admin_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.CONTACT_EMAIL],
            reply_to=[email],
        )
        msg_admin.send(fail_silently=False)

        # 2. Sender confirmation (HTML + plain text)
        confirm_body = (
            f"Hi {name},\n\n"
            "We received your message and will reply within 1–2 business days.\n\n"
            f"Subject: {subject}\n\n"
            "—\nUSA Content Hub"
        )
        confirm_html = render_to_string("blog/emails/contact_confirmation.html", {
            "name": name,
            "email": email,
            "subject": subject,
            "message": message,
        })
        msg_confirm = EmailMultiAlternatives(
            subject="We received your message — USA Content Hub",
            body=confirm_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
        )
        msg_confirm.attach_alternative(confirm_html, "text/html")
        msg_confirm.send(fail_silently=False)

        logger.info("Contact emails sent (admin + confirmation) to %s", email)
        return True
    except Exception as exc:
        logger.error(
            "SMTP ERROR — contact emails failed (name=%s email=%s): %s",
            name, email, exc,
        )
        return False
