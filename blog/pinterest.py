import base64
import logging
import os

import requests

logger = logging.getLogger(__name__)

_API = "https://api.pinterest.com/v5"
_OAUTH = "https://www.pinterest.com/oauth/"
_TOKEN_URL = f"{_API}/oauth/token"
_SCOPE = "boards:read,pins:write"


def _basic_header():
    cid = os.environ.get("PINTEREST_CLIENT_ID", "")
    csec = os.environ.get("PINTEREST_CLIENT_SECRET", "")
    encoded = base64.b64encode(f"{cid}:{csec}".encode()).decode()
    return {"Authorization": f"Basic {encoded}", "Content-Type": "application/x-www-form-urlencoded"}


def auth_url(redirect_uri):
    cid = os.environ.get("PINTEREST_CLIENT_ID", "")
    return (
        f"{_OAUTH}?client_id={cid}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={_SCOPE}"
    )


def exchange_code(code, redirect_uri):
    """Exchange OAuth code for access_token + refresh_token. Returns dict or None."""
    resp = requests.post(
        _TOKEN_URL,
        headers=_basic_header(),
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
        },
        timeout=15,
    )
    if resp.ok:
        return resp.json()
    logger.error("Pinterest token exchange failed: %s %s", resp.status_code, resp.text[:300])
    return None


def _refresh_token():
    """Try to get a new access_token using the stored refresh_token. Returns token string or None."""
    refresh = os.environ.get("PINTEREST_REFRESH_TOKEN", "")
    if not refresh:
        return None
    resp = requests.post(
        _TOKEN_URL,
        headers=_basic_header(),
        data={"grant_type": "refresh_token", "refresh_token": refresh},
        timeout=15,
    )
    if resp.ok:
        return resp.json().get("access_token")
    logger.error("Pinterest token refresh failed: %s %s", resp.status_code, resp.text[:300])
    return None


def _do_create_pin(token, board_id, payload):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return requests.post(f"{_API}/pins", headers=headers, json=payload, timeout=20)


def create_pin(article, site_url):
    """Create a Pinterest pin for the given article. Silently logs on failure."""
    access_token = os.environ.get("PINTEREST_ACCESS_TOKEN", "")
    board_id = os.environ.get("PINTEREST_BOARD_ID", "")

    if not access_token or not board_id:
        logger.warning(
            "Pinterest: skipping pin — PINTEREST_ACCESS_TOKEN or PINTEREST_BOARD_ID not set"
        )
        return

    cover = article.cover_image or "https://picsum.photos/seed/usacontenthub/1200/630"
    description = (article.meta_description or article.subtitle or article.title)[:500]

    payload = {
        "board_id": board_id,
        "title": article.title[:100],
        "description": description,
        "media_source": {"source_type": "image_url", "url": cover},
        "link": f"{site_url}/article/{article.slug}/",
    }

    resp = _do_create_pin(access_token, board_id, payload)

    if resp.status_code == 401:
        logger.info("Pinterest: access token expired, attempting refresh")
        new_token = _refresh_token()
        if new_token:
            resp = _do_create_pin(new_token, board_id, payload)
        else:
            logger.error("Pinterest: token refresh failed — pin not created for '%s'", article.slug)
            return

    if resp.ok:
        pin_id = resp.json().get("id", "unknown")
        logger.info("Pinterest: pinned '%s' (pin_id=%s)", article.slug, pin_id)
    else:
        logger.error(
            "Pinterest: failed to pin '%s' — %s %s",
            article.slug, resp.status_code, resp.text[:300],
        )
