"""IndexNow submission — instantly notify search engines of new/updated URLs.

IndexNow is supported by Bing, Yandex, Seznam, Naver and others (one ping is
shared across all participating engines). Google does not consume IndexNow, so
Google discovery still relies on the sitemap + Search Console.
"""
import logging
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)

ENDPOINT = "https://api.indexnow.org/indexnow"


def submit_url(url):
    """Ping IndexNow for a single absolute URL. Best-effort; never raises."""
    key = getattr(settings, "INDEXNOW_KEY", "")
    if not key or not url:
        return False

    site_url = getattr(settings, "SITE_URL", "").rstrip("/")
    host = urllib.parse.urlparse(site_url or url).netloc
    if not host or "localhost" in host or "127.0.0.1" in host:
        return False  # don't ping for local development

    params = urllib.parse.urlencode({
        "url": url,
        "key": key,
        "keyLocation": f"{site_url}/{key}.txt",
    })
    try:
        req = urllib.request.Request(f"{ENDPOINT}?{params}", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            logger.info("IndexNow: submitted %s (HTTP %s)", url, resp.status)
            return 200 <= resp.status < 300
    except Exception:
        logger.warning("IndexNow: failed to submit %s", url, exc_info=True)
        return False
