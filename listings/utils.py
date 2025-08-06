from django.shortcuts import redirect
from .models import Subscription

def premium_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        sub = getattr(request.user, 'subscription', None)
        if not sub or not sub.is_active():
            return redirect("pricing")
        return view_func(request, *args, **kwargs)
    return _wrapped_view