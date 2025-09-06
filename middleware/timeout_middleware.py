import signal
from django.conf import settings
from django.http import HttpResponse

class TimeoutException(Exception):
    pass

def handler(signum, frame):
    raise TimeoutException()

class RequestTimeoutMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.timeout = getattr(settings, 'REQUEST_TIMEOUT', 5)

    def __call__(self, request):
        signal.signal(signal.SIGALRM, handler)
        signal.alarm(self.timeout)
        try:
            response = self.get_response(request)
        except TimeoutException:
            return HttpResponse('Request timeout', status=504)
        finally:
            signal.alarm(0)
        return response
