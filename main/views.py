import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect

from main.forms import SellingSearchForm, SellingCreateForm
from main.selectors import list_user_active_selling, selling_count
from main.services import bgg_search_name


logger = logging.getLogger(__name__)


@login_required
def account_profile_view(request: WSGIRequest):
    ctx = {
        'user': request.user,
    }
    return render(request, 'main/account_profile.html', ctx)


@login_required
def account_selling_view(request: WSGIRequest):
    ctx = {
        'active': list_user_active_selling(request.user),
    }
    return render(request, 'main/account_selling.html', ctx)


@login_required
def account_selling_search_view(request: WSGIRequest):
    form = SellingSearchForm(request.POST or None)
    ctx = {'form': form}
    if request.method == "POST":
        if form.is_valid():
            results = bgg_search_name(form.cleaned_data['name'])
            ctx['results'] = results
            request.session['selling_search'] = results
            if not results:
                ctx['empty'] = True
    return render(request, 'main/account_selling_search.html', ctx)


@login_required
def account_selling_create_view(request: WSGIRequest, i: int):
    try:
        item = request.session['selling_search'][i]
    except (KeyError, IndexError) as exc:
        logger.info(f'Could not find search items during create for {request.user}')
        messages.error(request, 'No board game selected: search and select from results.')
        return redirect('account_selling_search')
    form = SellingCreateForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save(request.user, item)
            return redirect('account_selling')
    ctx = {
        'form': form,
        'item': item,
    }
    return render(request, 'main/account_selling_create.html', ctx)


def home_view(request: WSGIRequest):
    ctx = {
        'selling_cnt': selling_count()
    }
    return render(request, 'main/home.html', ctx)


def selling_view(request: WSGIRequest):
    ctx = {
    }
    return render(request, 'main/selling.html', ctx)
