from django.contrib.auth.models import User
from django.db import models
from website.apwan.helpers.database import unique_slugify
from website.apwan.models.service import Service

__author__ = 'Dean Gardiner'


class Payee(models.Model):
    class Meta:
        app_label = 'apwan'

    owner = models.ForeignKey(User)

    user = models.ForeignKey(Service, null=True)

    account_name = models.CharField(max_length=64, null=True, blank=True)
    account_id = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=32)  # TODO: Change to 'title' to match up with Recipient and Entity models
    slug = models.SlugField(max_length=32)

    def path(self):
        return '/account/payee/' + self.slug

    def save(self, **kwargs):
        unique_slugify(
            self, self.name,
            queryset=Payee.objects.all().filter(owner=self.owner)
        )
        super(Payee, self).save(kwargs)

    def dict(self):
        item = {
            'name': self.name,
            'slug': self.slug,
            'account_id': self.account_id,
            'account_name': self.account_name
        }

        if self.user:
            item['user'] = self.user.dict()
        else:
            item['user'] = None

        return item