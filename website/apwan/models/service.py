from django.contrib.auth.models import User
from django.db import models
from json_field import JSONField

__author__ = 'Dean Gardiner'


class Service(models.Model):
    class Meta:
        app_label = 'apwan'
        unique_together = ('service', 'service_id')

    SERVICE_WEPAY = 'wepay'
    SERVICE_BRAINTREE = 'braintree'
    SERVICES = (
        ('', "Invalid"),
        (SERVICE_WEPAY, "WePay"),
        (SERVICE_BRAINTREE, "Braintree"),
    )

    TYPE_PAYEE_USER = 1
    TYPES = (
        (0, "Invalid"),
        (TYPE_PAYEE_USER, "Payee User"),
    )

    LINK_TYPE_OAUTH = 1
    LINK_TYPE_KEY = 2
    LINK_TYPES = (
        (0, "Invalid"),
        (LINK_TYPE_OAUTH, "OAuth"),
        (LINK_TYPE_KEY, "Key"),
    )

    owner = models.ForeignKey(User, null=True)

    service = models.CharField(choices=SERVICES, default='', max_length=10)
    service_type = models.IntegerField(choices=TYPES, default=0)
    service_id = models.CharField(max_length=64, default="")

    link_type = models.IntegerField(choices=LINK_TYPES, default=0)
    data = JSONField()

    def name(self):
        return self.data.get('name', '')

    def email(self):
        if self.service == Service.SERVICE_WEPAY:
            return self.data['email']
        return None

    def valid(self):
        if self.service == Service.SERVICE_WEPAY:
            return 'access_token' in self.data
        raise NotImplementedError()

    def dict(self):
        # pylint: disable=E1101
        return {
            'service': self.service,
            'service_label': self.get_service_display(),

            'service_type': self.service_type,
            'service_type_label': self.get_service_type_display(),

            'service_id': self.service_id,

            'link_type': self.link_type,
            'link_type_label': self.get_link_type_display(),

            'name': self.name(),
            'email': self.email(),
        }
        # pylint: enable=E1101
