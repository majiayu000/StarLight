import logging
from typing import Callable, Optional, Type

from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

from logClient.common import Log

Log.log("requestLog.log")


# A middleware can be written as a function
def simple_middleware(get_response):
    # One-time configuration and initialization.

    def middleware(request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request_data = {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "body": request.body.decode("utf-8"),
        }
        # Todo: choose the parameters we need in headers
        logging.info(request_data)

        response = get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    return middleware


# It can be written as a class whose instances are callable, like this:
class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> None:
        request_data = {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "body": request.body.decode("utf-8"),
        }
        # Todo: choose the parameters we need in headers
        logging.info(request_data)

    def process_exception(
        self, request: HttpRequest, exception: Type[Exception]
    ) -> Optional[Type[Exception]]:
        try:
            raise exception
        except Exception as e:
            logging.exception("Unhandled Exception: " + str(e))
        return exception


# Given MiddlewareMixin has been deprecated,
# let's write a middleware from scratch
class RequestLoggingMiddleware:
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        request_data = {
            "method": request.method,
            "path": request.path,
            "headers": dict(request.headers),
            "body": request.body.decode("utf-8"),
        }
        logging.info(request_data)

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        # logger.info(f'Response: {response.status_code}')

        return response
