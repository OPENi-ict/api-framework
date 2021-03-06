__author__ = 'alvertisjo'

from django.db import models

from OPENiapp.APIS.models import GenericModel
from OPENiapp.APIS.Products_and_Services.Card.models import OpeniCard


class OpeniRefund(GenericModel):
    # id is missing because it is the default
    target_id = models.TextField()    #The id of the object where this payment applies	string
    card_id = models.ForeignKey(OpeniCard)    #The id of the used payment method	string
    amount = models.FloatField()    #The amount of money returned	string
    currency = models.TextField()    #The used currency where the refund has been done	string
    reason = models.TextField()
