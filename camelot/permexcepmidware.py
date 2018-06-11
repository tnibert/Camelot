from .controllers.utilities import PermissionException, AlreadyExistsException
from django.http import HttpResponseRedirect
from django.http.response import Http404
from django.shortcuts import render
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class RedirectToRefererResponse(HttpResponseRedirect):
    def __init__(self, request, *args, **kwargs):
        redirect_to = request.META.get('HTTP_REFERER', '/')
        super(RedirectToRefererResponse, self).__init__(
            redirect_to, *args, **kwargs)

class HandleBusinessExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, PermissionException):
            raise Http404
        elif isinstance(exception, AlreadyExistsException):
            #message = "Invalid operation %s" % unicode(exception)
            #messages.error(request, message)
            #return RedirectToRefererResponse(request)
            pass
