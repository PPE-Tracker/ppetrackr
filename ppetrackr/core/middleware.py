import pytz
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user and request.user.is_authenticated and request.user.timezone:
            tzname = request.user.timezone
            timezone.activate(tzname)
        else:
            timezone.deactivate()
        return self.get_response(request)
