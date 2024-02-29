import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import render, redirect, get_object_or_404

from main.forms import SellingSearchForm, SellingForm
from main.models import Listing, Game
from main.selectors import list_user_active_selling, for_sale
from main.services import bgg_search_name, scrape_game_by_id

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
    form = SellingForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save(request.user, item)
            return redirect('account_selling')
    ctx = {
        'form': form,
        'item': item,
    }
    return render(request, 'main/account_selling_create.html', ctx)


@login_required
def account_selling_edit_view(request: WSGIRequest, slug: str):
    listing = get_object_or_404(Listing, slug=slug, user=request.user)
    form = SellingForm(request.POST or None, instance=listing)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            return redirect('account_selling')
    ctx = {
        'form': form,
        'listing': listing,
    }
    return render(request, 'main/account_selling_edit.html', ctx)


@login_required
def account_selling_expand_view(request: WSGIRequest, slug: str):
    listing = get_object_or_404(Listing, slug=slug, user=request.user)

    # create expansion otherwise show form
    if (expand_search := request.session.get('expand_search')) and (sel := request.GET.get('i')):
        exp = expand_search[int(sel)]
        game_data = scrape_game_by_id(exp['id'])
        game, _ = Game.objects.update_or_create(
            id=game_data.pop('id'),
            defaults=game_data
        )
        listing.bundle.add(game)
        logger.info(f'Added {game} to {listing}')
        return redirect('account_selling')

    # nothing to add, show form to search
    form = SellingSearchForm(request.POST or None)
    ctx = {
        'form': form,
        'listing': listing,
    }
    if request.method == "POST":
        if form.is_valid():
            results = bgg_search_name(form.cleaned_data['name'])
            ctx['results'] = results
            request.session['expand_search'] = results
            if not results:
                ctx['empty'] = True
    return render(request, 'main/account_selling_expand.html', ctx)


@login_required
def account_selling_expand_remove_view(request: WSGIRequest, slug: str, pk: int):
    listing = get_object_or_404(Listing, slug=slug, user=request.user)
    game = get_object_or_404(Game, id=pk)
    listing.bundle.remove(game)
    listing.save()
    logger.info(f'Removed {game} from {listing} bundle')
    return redirect('account_selling')


def home_view(request: WSGIRequest):
    ctx = {
        'for_sale_cnt': for_sale().count(),
    }
    return render(request, 'main/home.html', ctx)


def for_sale_view(request: WSGIRequest):
    ctx = {
        'for_sale': for_sale(),
    }
    return render(request, 'main/for_sale.html', ctx)


def for_sale_detail_view(request: WSGIRequest, slug: str):
    listing = get_object_or_404(Listing, slug=slug)
    ctx = {
        'listing': listing,
    }
    return render(request, 'main/for_sale_detail.html', ctx)
