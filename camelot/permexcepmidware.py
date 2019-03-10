from .controllers.utilities import PermissionException, AlreadyExistsException, DiskExceededException
from django.http import HttpResponseRedirect, JsonResponse
from django.http.response import Http404
from django.shortcuts import render
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from .logs import log_exception


class RedirectToRefererResponse(HttpResponseRedirect):
    def __init__(self, request, *args, **kwargs):
        redirect_to = request.META.get('HTTP_REFERER', '/')
        super(RedirectToRefererResponse, self).__init__(
            redirect_to, *args, **kwargs)


class HandleBusinessExceptionMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        # log the exception
        log_exception(__name__, exception)

        # process appropriately
        if isinstance(exception, PermissionException):
            raise Http404
        elif isinstance(exception, AlreadyExistsException):
            #message = "Invalid operation %s" % unicode(exception)
            #messages.error(request, message)
            #return RedirectToRefererResponse(request)
            pass
        elif isinstance(exception, DiskExceededException):
            # todo: test in api tests
            return JsonResponse({'message': "Not enough space to store data"}, status=507)
