"""
Email a tech-blog draft to the reviewer for approval.

Usage:
    python3 send_review_email.py drafts/<slug>.json

Sends the full article (rendered HTML) to REVIEW_EMAIL so the reviewer can
read it in their inbox, then come back to Claude Code and say yes/no.
Uses the same EMAIL_* settings as the site (writeflow/settings.py).
If SMTP isn't configured yet, prints the email to the console instead.
"""
import json
import os
import re
import sys

# Standalone script — load .env ourselves (manage.py normally does this)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "writeflow.settings")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django

django.setup()

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

REVIEW_EMAIL = os.environ.get("REVIEW_EMAIL", "tusharlimbasiya200@gmail.com")
WORDS_PER_MINUTE = 200


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with open(sys.argv[1], encoding="utf-8") as f:
        draft = json.load(f)

    slug = draft["slug"]
    text = re.sub(r"<[^>]+>", " ", draft["content"])
    words = len(text.split())
    read_time = max(1, round(words / WORDS_PER_MINUTE))
    tags = ", ".join(draft.get("tags", []))

    subject = f"📝 Review: {draft['title']}"
    live_url = f"{settings.SITE_URL}/article/{slug}/"
    local_url = f"http://127.0.0.1:8799/article/{slug}/"

    html = f"""
    <div style="max-width:680px;margin:0 auto;font-family:Georgia,serif;line-height:1.7;color:#1a1a1a">
      <div style="background:#7c3aed;color:#fff;padding:16px 24px;border-radius:8px 8px 0 0;font-family:Arial,sans-serif">
        <strong>🧠 Tech Pulse — Draft ready for your review</strong>
      </div>
      <div style="border:1px solid #e5e7eb;border-top:none;padding:24px;border-radius:0 0 8px 8px">
        <p style="font-family:Arial,sans-serif;font-size:13px;color:#6b7280;margin-top:0">
          {words} words · ~{read_time} min read · tags: {tags}<br>
          slug: <code>{slug}</code>
        </p>
        <h1 style="margin:8px 0 4px">{draft['title']}</h1>
        <p style="font-size:18px;color:#4b5563;margin-top:0"><em>{draft.get('subtitle', '')}</em></p>
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0">
        {draft['content']}
        <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0">
        <p style="font-family:Arial,sans-serif;font-size:14px;background:#f3f4f6;padding:14px;border-radius:6px">
          ✅ <strong>To approve:</strong> go back to Claude Code and say <strong>yes</strong> — the article
          will then be pushed and go live at<br><a href="{live_url}">{live_url}</a><br>
          👀 Local preview (while runserver is on): <a href="{local_url}">{local_url}</a><br>
          ✏️ Want changes? Tell Claude what to edit.&nbsp; ❌ Say no to discard.
        </p>
      </div>
    </div>
    """
    plain = (
        f"DRAFT READY FOR REVIEW\n\n{draft['title']}\n{draft.get('subtitle', '')}\n\n"
        f"{words} words, ~{read_time} min read, tags: {tags}\n\n{text[:2000]}\n\n"
        f"Approve in Claude Code (say yes) to publish at {live_url}"
    )

    if settings.EMAIL_BACKEND.endswith("console.EmailBackend") or not getattr(
        settings, "EMAIL_HOST_PASSWORD", ""
    ):
        print("⚠ SMTP not configured (EMAIL_HOST / EMAIL_HOST_PASSWORD missing in .env).")
        print(f"  Would have emailed {REVIEW_EMAIL}: {subject}")
        print("  → Add your Gmail App Password to .env to enable real sending.")
        return

    msg = EmailMultiAlternatives(subject, plain, settings.DEFAULT_FROM_EMAIL, [REVIEW_EMAIL])
    msg.attach_alternative(html, "text/html")
    msg.send()
    print(f"  ✓ Review email sent to {REVIEW_EMAIL}: {subject}")


if __name__ == "__main__":
    main()
