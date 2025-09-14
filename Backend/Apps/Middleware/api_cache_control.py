from django.utils.cache import add_never_cache_headers


class APINoCacheMiddleware:
    """
    Middleware to prevent caching of API responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check if this is an API request
        if request.path.startswith("/api/"):
            # Add headers to prevent caching
            add_never_cache_headers(response)
            response["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"

        return response
