from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render


def accounts_profile_view(request: WSGIRequest):
    ctx = {
        'user': request.user,
    }
    return render(request, 'main/account_profile.html', ctx)


def accounts_selling_view(request: WSGIRequest):
    ctx = {
        'user': request.user,
    }
    return render(request, 'main/account_profile.html', ctx)


def home_view(request: WSGIRequest):
    ctx = {
    }
    return render(request, 'main/home.html', ctx)
