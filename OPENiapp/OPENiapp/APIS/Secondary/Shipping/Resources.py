from tastypie.authorization import DjangoAuthorization
from .models import OpeniShipping

from OPENiapp.APIS.OpeniGenericResource import GenericResource, GenericMeta
from OPENiapp.APIS.OPENiAuthorization import Authorization
from OPENiapp.APIS.OPENiAuthentication import Authentication

class ShippingResource(GenericResource):
    class Meta(GenericMeta):
        queryset = OpeniShipping.objects.all()
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        resource_name = 'Shipping'
        authentication = Authentication()
        authorization = Authorization()