from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.timezone import now

CONDITION_NEW = 'New'
CONDITION_GOOD = 'Good'
CONDITION_USED = 'Used'
CONDITION_PARTS = 'Parts'
CONDITION_OTHER = 'Other'

CONDITION_CHOICES = [
    (CONDITION_NEW, 'New: still in shrink wrap or unpunched'),
    (CONDITION_GOOD, 'Good: only played a few times or no damage'),
    (CONDITION_USED, 'Used: wear and tear showing or box has some dents'),
    (CONDITION_PARTS, 'Parts: components missing or broken'),
    (CONDITION_OTHER, 'Other: specify in comments'),
]


class TimestampModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Game(models.Model):
    name = models.CharField(max_length=255)
    year = models.IntegerField(
        validators=[MinValueValidator(-2500), MaxValueValidator(now().year + 1)])
    url = models.CharField(max_length=255)
    rank = models.PositiveIntegerField()
    rating = models.PositiveIntegerField()
    subtype = models.CharField(max_length=50)

    # details
    scraped_at = models.DateTimeField(null=True, blank=True)
    img = models.CharField(max_length=250, null=True, blank=True)
    pitch = models.CharField(max_length=256, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    # time
    min_play_time = models.PositiveSmallIntegerField(null=True, blank=True)
    max_play_time = models.PositiveSmallIntegerField(null=True, blank=True)
    # players
    min_players = models.PositiveSmallIntegerField(null=True, blank=True)
    max_players = models.PositiveSmallIntegerField(null=True, blank=True)
    rec_min_players = models.PositiveSmallIntegerField(null=True, blank=True)
    rec_max_players = models.PositiveSmallIntegerField(null=True, blank=True)
    best_min_players = models.PositiveSmallIntegerField(null=True, blank=True)
    best_max_players = models.PositiveSmallIntegerField(null=True, blank=True)
    # weight
    weight_avg = models.FloatField(null=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.year})'

    @property
    def bgg_link(self):
        return f'https://www.boardgamegeek.com/boardgame/{self.id}'

    def players_fmt(self) -> str:
        """Show players on game detail page"""
        cnts = []
        for cnt in range(1, 9):
            if self.best_min_players <= cnt <= self.best_max_players:
                cnts.append(f'<strong style="font-size: 1.1em">{cnt}</strong>')
            elif self.rec_min_players <= cnt <= self.rec_max_players:
                cnts.append(f'{cnt}')
            elif self.min_players <= cnt <= self.max_players:
                cnts.append(f'<small class="text-muted">{cnt}</small>')
        return mark_safe('&nbsp;'.join(cnts))

    def age_fmt(self) -> str:
        if self.rec_min_age:
            return f'{self.rec_min_age}+'
        elif self.min_age:
            return f'{self.min_age}+'
        return ''


class Listing(TimestampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='listings')

    price = models.IntegerField(validators=[MinValueValidator(100), MaxValueValidator(20_000)])
    is_negotiable = models.BooleanField(default=True)
    is_shipping = models.BooleanField(default=False)
    condition = models.CharField(max_length=50, choices=CONDITION_CHOICES, default=CONDITION_GOOD)
    comment = models.TextField(blank=True, null=True)

    is_hidden = models.BooleanField(default=False)
    is_sold = models.BooleanField(default=False)
    sold_comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f'{self.game.name} ({self.game.year})'
