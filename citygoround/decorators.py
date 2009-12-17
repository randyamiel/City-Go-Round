import types
from django.conf import settings
from django.http import Http404, HttpResponseForbidden
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache
from .models import TransitApp, Agency
from .utils.httpbasicauth import authenticate_request
from .utils.progressuuid import is_progress_uuid_valid
from .utils.view import method_not_allowed
from .utils.memcache import key_for_view_function, key_for_request

def memcache_view_response(*args, **kwargs):
    """Memcache the entire response object of the view. 
    Do so unconditionally, regardless of any parameters sent to the view.
    
    Optional named parameters:
        time = <memcache expiration time in seconds>
        namespace = <memcache namespace>
    """
    time = kwargs.get('time', 0)
    namespace = kwargs.get('namespace', None)
    
    def decorator(view_function):
        def wrapper(request, *wrapped_args, **wrapped_kwargs):
            memcache_key = key_for_view_function(view_function)
            response = memcache.get(memcache_key, namespace = namespace)
            if response is None:
                response = view_function(request, *wrapped_args, **wrapped_kwargs)
                if not settings.RUNNING_APP_ENGINE_LOCAL_SERVER:
                    memcache.set(memcache_key, response, time = time, namespace = namespace)
            return response
        wrapper.__name__ = view_function.__name__
        wrapper.__module__ = view_function.__module__
        return wrapper        
        
    # Was memcache_view_response called with no parameters? If so,
    # python runtime directly hands us the function to decorate.
    if (len(args) == 1) and (type(args[0]) is types.FunctionType):
        return decorator(args[0])
        
    # memcache_view_response was called WITH parameters. This means
    # that we must return a function that will _in turn_ take the
    # function to decorate.
    return decorator
    
def memcache_parameterized_view_response(*args, **kwargs):
    """Memcache the entire response object of the view. 
    Do so conditionally, taking into account the URL, request method, and parameters in GET or POST.
    
    Optional named parameters:
        time = <memcache expiration time in seconds>
        namespace = <memcache namespace>
    """
    time = kwargs.get('time', 0)
    namespace = kwargs.get('namespace', None)
    
    def decorator(view_function):
        def wrapper(request, *wrapped_args, **wrapped_kwargs):
            memcache_key = key_for_request(request)
            response = memcache.get(memcache_key, namespace = namespace)          
            if response is None:
                response = view_function(request, *wrapped_args, **wrapped_kwargs)
                if not settings.RUNNING_APP_ENGINE_LOCAL_SERVER:                
                    memcache.set(memcache_key, response, time = time, namespace = namespace)
            return response
        wrapper.__name__ = view_function.__name__
        wrapper.__module__ = view_function.__module__
        return wrapper
        
    # Was memcache_parameterized_view_response called with no parameters? If so,
    # python runtime directly hands us the function to decorate.
    if (len(args) == 1) and (type(args[0]) is types.FunctionType):
        return decorator(args[0])

    # memcache_parameterized_view_response was called WITH parameters. This means
    # that we must return a function that will _in turn_ take the
    # function to decorate.
    return decorator

def _requires_method(view_function, method):
    def wrapper(request, *args, **kwargs):
        if request.method != method:
            return method_not_allowed("Must be called with %s." % method)
        return view_function(request, *args, **kwargs)
    wrapper.__name__ = view_function.__name__
    wrapper.__module__ = view_function.__module__
    return wrapper

def requires_GET(view_function):
    return _requires_method(view_function, method = "GET")
    
def requires_POST(view_function):
    return _requires_method(view_function, method = "POST")
    
def requires_http_basic_authentication(view_function, correct_username, correct_password, realm = None):
    def wrapper(request, *args, **kwargs):
        authentication_response = authenticate_request(request, correct_username, correct_password, realm)
        if authentication_response is not None:
            return authentication_response
        return view_function(request, *args, **kwargs)   
    wrapper.__name__ = view_function.__name__
    wrapper.__module__ = view_function.__module__
    return wrapper     

def requires_valid_transit_app_slug(view_function):
    def wrapper(request, transit_app_slug, *args, **kwargs):
        transit_app = TransitApp.transit_app_for_slug(transit_app_slug)
        if transit_app is not None:
            return view_function(request, transit_app, *args, **kwargs)
        else:
            raise Http404
    wrapper.__name__ = view_function.__name__
    wrapper.__module__ = view_function.__module__
    return wrapper
    
def requires_valid_progress_uuid(view_function):
    def wrapper(request, progress_uuid, *args, **kwargs):
        if not is_progress_uuid_valid(request, progress_uuid):
            raise Http404
        return view_function(request, progress_uuid, *args, **kwargs)
    wrapper.__name__ = view_function.__name__
    wrapper.__module__ = view_function.__module__
    return wrapper
    
def requires_valid_agency_key_encoded(view_function):
    def wrapper(request, key_encoded, *args, **kwargs):
        try:
            agency = Agency.get(db.Key(key_encoded.strip()))
        except db.Error:
            raise Http404
        if agency is None:
            raise Http404
        return view_function(request, agency = agency, *args, **kwargs)
    wrapper.__name__ = view_function.__name__
    wrapper.__module__ = view_function.__module__
    return wrapper

def requires_google_admin_login(view_function):
    def wrapper(request, *args, **kwargs):
        if not users.is_current_user_admin():
            return HttpResponseForbidden()
        else:
            return view_function(request, *args, **kwargs)
    wrapper.__name__ = view_function.__name__
    wrapper.__module__ = view_function.__module__
    return wrapper
