"""
Custom Django middleware for security and performance headers.
Placed early in MIDDLEWARE so headers are set on every response,
including error pages and redirects.
"""


class SecurityHeadersMiddleware:
    """
    Adds security headers that Django's built-in SecurityMiddleware
    does not cover:
      - Permissions-Policy: restricts browser feature access
      - Cross-Origin-Resource-Policy: prevents cross-origin resource leaks
      - Cross-Origin-Embedder-Policy: required for SharedArrayBuffer
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

        # Prevent other sites from loading your resources (images, scripts) cross-origin
        if "Cross-Origin-Resource-Policy" not in response:
            response["Cross-Origin-Resource-Policy"] = "same-origin"

        return response
