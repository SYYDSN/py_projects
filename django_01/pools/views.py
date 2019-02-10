# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from . import rpc_client_auth

# Create your views here.



def index(request):
    rpc_client_auth.check_request(request)
    return HttpResponse("Hello world! this is pools's index page")
