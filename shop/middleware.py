# middleware.py
import logging


class LogRequestsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger("django")

    def __call__(self, request):
        self.logger.info(f"Request: {request.method} {request.path}")
        self.logger.info(f"Referer: {request.META.get('HTTP_REFERER', 'Unknown')}")
        self.logger.info(f"Headers: {request.headers}")
        return self.get_response(request)
