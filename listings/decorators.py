from django.http import HttpResponseForbidden

def seller_or_agent_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role in ['seller', 'agent']:
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("403: You do not have permission to access this page.")
    return _wrapped_view