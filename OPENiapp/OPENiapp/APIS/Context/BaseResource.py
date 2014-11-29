import ast

from django.db import transaction
from tastypie import fields
from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource
from django.contrib.auth.models import User

from OPENiapp.APIS.Context.models import OpeniContext
from OPENiapp.Providers.generic import execution


__author__ = 'amertis'


class ContextAwareResource(ModelResource):
    from OPENiapp.APIS.Context.Resources import ContextResource

    context = fields.ToOneField(ContextResource, 'context', full=True)

    # TODO remove this only to openigenericresource
    def cbs_handling(self, request, **kwargs):

        pathSplit = request.path.split('/')

        pathSplitLength = len(pathSplit)
        version = pathSplit[1]
        resource_name = pathSplit[2].lower()
        id = ""
        connection = ""
        if pathSplitLength > 3:
            id = pathSplit[3]
            if pathSplitLength > 4:
                connection = pathSplit[4].lower()

        params = ""
        for each in request.REQUEST.dicts[1]:
            if each != 'user' and each != 'api_key' and each != 'cbs' and each != 'limit' and each != 'offset':
                params = request.REQUEST.dicts[1]

        # Try to parse the parameters of the call
        try:
            user = request.GET.get("user")
            u = User.objects.filter(username=user)
        except:
            # To-Do: Make an appropriate error response!
            return [{"error": "User is not authenticated. Please refer to the documentation"}]

        # Try to get the cbs required for the call
        try:
            cbs = ast.literal_eval(request.GET.get("cbs"))
        except:
            return [{"CBS": "Only Cloudlet Objects were retrieved. No additional CBS were selected."}]

        # Try to parse the parameters of the call
        #try:
        #    params = ast.literal_eval(request.GET.get("params"))
        #except:
        #    params = ""

        request_method = request.META['REQUEST_METHOD'].lower()
        method = request_method + '_' + resource_name
        # If there is a connection in the url then add it to the method
        if connection != "":
            method += '_' + connection
            # If there is an id in the url then make the methods plural.
        if id == "":
            if (resource_name == 'status'):
                method += 'e'
            if (resource_name != 'rsvp'):
                method += 's'

        executable = execution(u, cbs, method, id, params)
        return executable.make_all_connections()


    @transaction.atomic
    def obj_create(self, bundle, **kwargs):
        bundle = self.full_hydrate(bundle)

        try:
            if not bundle.request.GET.get("cbs"):
                raise AttributeError
                cbs_return = self.cbs_handling(bundle.request, **kwargs)
            #return self.create_response(bundle.request, cbs_return)
        except:
            pass

        if bundle.obj.context is None:
            raise BadRequest("context attribute is not defined")
        bundle.obj.context.save()
        bundle.obj.context_id = bundle.obj.context.id
        bundle.obj.save()
        bundle.obj.context.objectid = bundle.obj.id
        # bundle.obj.context.save(update_fields=["objectid"])
        bundle.obj.context.save()
        return bundle


    @transaction.atomic
    def obj_update(self, bundle, **kwargs):

        try:
            if not bundle.request.GET.get("cbs"):
                raise AttributeError
            cbs_return = self.cbs_handling(bundle.request, **kwargs)
            #return self.create_response(bundle.request, cbs_return)
        except:
            pass

        if 'id' not in bundle.data:
            raise BadRequest("id property not found")
        bundle = self.full_hydrate(bundle)
        if bundle.obj.context.id is None:
            raise BadRequest("context id not found")
        bundle.obj.context.save()
        bundle.obj.save()
        return bundle

        # def obj_delete(self, bundle, **kwargs):
    #     return bundle
    @transaction.atomic
    def obj_delete(self, bundle, **kwargs):

        try:
            if not bundle.request.GET.get("cbs"):
                raise AttributeError
            cbs_return = self.cbs_handling(bundle.request, **kwargs)
            #return self.create_response(bundle.request, cbs_return)
        except:
            pass

        if 'pk' not in kwargs:
            raise BadRequest("no pk parameter found")
        try:
            pk = int(kwargs['pk'])
        except ValueError, e:
            raise BadRequest("invalid pk parameter")
        bundle = self.full_hydrate(bundle)
        type(bundle.obj).objects.filter(id=pk).delete()
        OpeniContext.objects.filter(objectid=pk).delete()
        return bundle