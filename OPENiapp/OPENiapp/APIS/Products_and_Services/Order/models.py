from OPENiapp.OPENiapp.APIS.Context.models import OpeniContextAwareModel
from OPENiapp.OPENiapp.APIS.Products_and_Services.Product.models import OpeniProduct
from OPENiapp.OPENiapp.APIS.Products_and_Services.Shop.models import OpeniShop
from OPENiapp.OPENiapp.APIS.Products_and_Services.Shop.models import OpeniShop


__author__ = 'mpetyx'


from django.db import models


class OpeniOrder(OpeniContextAwareModel):
    # id is missing because it is the default
    url = models.TextField()
    object_type = models.TextField()
    service = models.TextField()
    From = models.TextField()
    list = models.ManyToManyField(OpeniProduct)
    target_id = models.OneToManyField(OpeniShop)
    total_amount = models.TextField()
    currency = models.TextField()
    vat = models.TextField()