# Generated by Django 5.0.2 on 2024-02-28 16:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_alter_game_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='bundle',
            field=models.ManyToManyField(related_name='bundle', to='main.game'),
        ),
    ]
