from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect


def onboard_required(func):
    """
    Decorator for views that checks that the user has onboarded,
    if not it will redirect to the onboard page.

    This decorator must be called "after" login_required decorator
    """
    # TODO: it would be better to incorporate login_required in this
    # decorator itself, maybe just use `user_passes_test`

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        print(request.user.is_onboarded)
        if not request.user.is_onboarded:
            messages.error(
                request, "Please complete your onboarding steps to continue forward.",
            )
            return redirect("onboard_view")
        return func(request, *args, **kwargs)

    return wrapper


def onboard_pending(func):
    """
    Decorator for views that checks that the user has not yet onboarded,
    if not it will redirect to the home page with an error message.

    This decorator needs to be called "after" login_required decorator
    """

    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_onboarded:
            messages.error(
                request,
                "You have already onboarded. If you need more help, please contact our support.",
            )
            return redirect("home_view")
        return func(request, *args, **kwargs)

    return wrapper
