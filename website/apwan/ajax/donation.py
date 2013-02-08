from dajaxice.decorators import dajaxice_register
from django.core.urlresolvers import reverse
from django.utils import simplejson
from website.apwan.ajax.utils import (
    cors_response,
    validate_int, validate_float,
    build_error, ERROR
)
from website.apwan.core.payment import wepay
from website.apwan.models.entity import Entity
from website.apwan.models.payee import Payee
from website.apwan.models.service import Service
from website.settings import build_url

__author__ = 'Dean Gardiner'


@dajaxice_register(method='GET', name='donation.create')
def create(request, recipient_id, entity_id, amount):
    # Check Parameter Value Types
    recipient_id, success = validate_int(recipient_id)
    if not success:
        return cors_response(
            build_error(ERROR.INVALID_PARAMETER, parameter='recipient_id'))

    entity_id, success = validate_int(entity_id)
    if not success:
        return cors_response(
            build_error(ERROR.INVALID_PARAMETER, parameter='entity_id'))

    amount, success = validate_float(amount)
    if not success:
        return cors_response(
            build_error(ERROR.INVALID_PARAMETER, parameter='amount'))
    if amount <= 0:
        return cors_response(
            build_error(ERROR.INVALID_PARAMETER, parameter='amount'))

    # Get entity
    entity = Entity.objects.filter(pk=entity_id)
    if len(entity) != 1:
        return cors_response(
            build_error(ERROR.INVALID_PARAMETER, parameter='entity_id'))
    entity = entity[0]

    # Get recipient from entity
    # (this will also confirm the entity and recipient are linked)
    recipient = entity.recipient.filter(pk=recipient_id)
    if len(recipient) != 1:
        return cors_response(
            build_error(ERROR.INVALID_PARAMETER, parameter='recipient_id'))
    recipient = recipient[0]

    payee = recipient.payee
    if payee is None or payee.user is None:
        return cors_response(
            build_error(ERROR.DONATION.NO_PAYEE))

    if payee.user.service == Service.SERVICE_WEPAY:
        donation, checkout_url = wepay.donation_create(
            entity, recipient, payee, amount,
            redirect_uri=build_url(request,
                                   reverse('donate-complete',
                                           args=[payee.user.service])),
            callback_uri=build_url(request,
                                   reverse('callback-wepay-checkout'))
        )

        if checkout_url:
            return cors_response(simplejson.dumps({
                'checkout_url': checkout_url,
                'success': True
            }))
        return cors_response(build_error(ERROR.DONATION.SERVICE_FAILED))

    return cors_response(build_error(ERROR.NOT_IMPLEMENTED))
