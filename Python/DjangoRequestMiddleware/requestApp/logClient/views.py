from django.shortcuts import render
from django.http import HttpResponse
from .middleware.request_log import RequestLoggingMiddleware


# Create your views here.

def index(request):
    return HttpResponse("Hello World")