from django.http import HttpResponse
from django.shortcuts import render
# from .task import add
import logging


# Create your views here.
def index(request):
    print("ff")
    logger = logging.getLogger("loggers")
    message = {"message": "user visits index()"}
    logger.info(message)
    return HttpResponse("hello")
