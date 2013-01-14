from django.db import models
from website.apwan.models.recipient import Recipient

__author__ = 'Dean Gardiner'


class Entity(models.Model):
    class Meta:
        app_label = 'apwan'
        verbose_name_plural = 'entities'

    TYPE_TVSHOW = 0
    TYPE_MOVIE = 1
    TYPE_MUSIC = 2
    TYPE_GAME = 3

    TYPES = (
        (TYPE_TVSHOW, "TV Show"),
        (TYPE_MOVIE, "Movie"),
        (TYPE_MUSIC, "Music"),
        (TYPE_GAME, "Game"),
    )

    recipient = models.ManyToManyField(Recipient)

    parent = models.ForeignKey('self', null=True)

    # for TYPE_TVSHOW, TYPE_MOVIE, TYPE_GAME
    title = models.CharField(max_length=64, null=True)

    # for TYPE_MUSIC
    artist = models.CharField(max_length=64, null=True)
    album = models.CharField(max_length=64, null=True)
    track = models.CharField(max_length=64, null=True)

    image = models.CharField(max_length=64, null=True)
    type = models.IntegerField(choices=TYPES)
    suggested_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def dict(self):
        dict = {
            'id': self.id,
            'image': self.image,
            'type': self.type
        }
        if self.type == self.TYPE_MUSIC:
            dict['artist'] = self.artist
            dict['album'] = self.album
            dict['track'] = self.track
        else:
            dict['title'] = self.title

        return dict