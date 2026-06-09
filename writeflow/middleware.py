"""
Custom Django middleware for security and performance headers.
Placed early in MIDDLEWARE so headers are set on every response,
including error pages and redirects.
"""


class SecurityHeadersMiddleware:
    """
    Adds security headers that Django's built-in SecurityMiddleware
    does not cover.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Prevent browser from granting camera/mic/geolocation without user gesture
        if "Permissions-Policy" not in response:
            response["Permissions-Policy"] = (
                "camera=(), microphone=(), geolocation=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )

        if "X-Permitted-Cross-Domain-Policies" not in response:
            response["X-Permitted-Cross-Domain-Policies"] = "none"

        if "Cross-Origin-Opener-Policy" not in response:
            response["Cross-Origin-Opener-Policy"] = "same-origin"

        if "Cross-Origin-Resource-Policy" not in response:
            response["Cross-Origin-Resource-Policy"] = "same-origin"

        if request.path.startswith(("/admin/", "/accounts/")):
            response["Cache-Control"] = "no-store, max-age=0"
        elif (
            request.method in {"GET", "HEAD"}
            and response.status_code == 200
            and "Set-Cookie" not in response
            and not request.path.startswith(("/contact/", "/csrf/", "/newsletter/", "/api/"))
        ):
            response["Cache-Control"] = "public, max-age=60, s-maxage=300, stale-while-revalidate=86400"

        return response
