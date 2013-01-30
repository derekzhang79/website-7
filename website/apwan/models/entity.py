from django.db import models

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

    recipient = models.ManyToManyField('Recipient')

    parent = models.ForeignKey('self', null=True)

    # for TYPE_TVSHOW, TYPE_MOVIE, TYPE_GAME
    title = models.CharField(max_length=64, null=True)

    # for TYPE_MOVIE
    year = models.IntegerField(max_length=4, null=True)

    # for TYPE_MUSIC
    artist = models.CharField(max_length=64, null=True)
    album = models.CharField(max_length=64, null=True)
    track = models.CharField(max_length=64, null=True)

    # Search fields
    s_title = models.CharField(max_length=64, null=True)
    s_artist = models.CharField(max_length=64, null=True)
    s_album = models.CharField(max_length=64, null=True)
    s_track = models.CharField(max_length=64, null=True)

    image = models.CharField(max_length=64, null=True)
    type = models.IntegerField(choices=TYPES)
    suggested_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True)

    def dict(self, full=False):
        item = {
            'id': self.id,
            'image': self.image,
            'type': self.type
        }
        if self.type == self.TYPE_MUSIC:
            item['artist'] = self.artist
            item['album'] = self.album  # TODO: don't set album or track if None, This could require changes
            item['track'] = self.track  # in extension and website js to check if album or track is included.
        else:
            item['title'] = self.title

            if self.type == self.TYPE_MOVIE:
                item['year'] = self.year

        if full:
            item['recipients'] = []
            for re in self.recipient.all():
                item['recipients'].append(re.dict())

        return item

    def __unicode__(self):
        if self.type == Entity.TYPE_MUSIC:
            if self.track:
                return "[%s] [Track] %s - %s - %s" % (Entity.TYPES[self.type][1], self.artist, self.album, self.track)
            elif self.album:
                return "[%s] [Album] %s - %s" % (Entity.TYPES[self.type][1], self.artist, self.album)
            else:
                return "[%s] [Artist] %s" % (Entity.TYPES[self.type][1], self.artist)
        else:
            return self.title