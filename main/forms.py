from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import User
from django.utils.timezone import now

from main.models import Listing, Game
from main.services import scrape_game_by_id


class SellingSearchForm(forms.Form):

    name = forms.CharField(
        label="Name of the board game?",
        max_length=80,
        required=True,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Search'))


class SellingCreateForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = ['price', 'condition', 'comment', 'is_negotiable', 'is_shipping']
        labels = {
            'price': 'Asking Price (in Rands)',
            'condition': 'Select the condition of the board game',
            'comment': 'Add some extra details or sweeteners',
            'is_negotiable': 'I am willing to negotiate on the price',
            'is_shipping': 'I will pay for the shipping',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit'))

    def save(self, user: User, item: dict, commit=True):
        self.instance.user = user
        game_data = scrape_game_by_id(item['id'])
        game, _ = Game.objects.update_or_create(
            id=item.pop('id'),
            defaults=game_data
        )
        self.instance.game = game
        super().save(commit)
