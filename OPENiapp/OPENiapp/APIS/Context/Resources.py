import json
import re

from django.conf.urls import url
# from django.db import transaction
from django.utils.datastructures import MultiValueDictKeyError
from tastypie import fields
from tastypie.exceptions import BadRequest
from tastypie.resources import Resource, ModelResource
from tastypie.utils import trailing_slash
from datetime import datetime
from .models import OpeniContext, LocationVisit, GroupFriend, Group

__author__ = 'amertis'


def ValuesQuerySetToDict(vqs):
    return [item for item in vqs]


from django.forms.models import model_to_dict


def get_fields(clz):
    fields = clz._meta.get_all_field_names()
    fields.remove("context")
    fields.remove("id")
    return fields


def convert_to_dbfields(clz, data):
    prefix = re.sub('(?!^)([A-Z]+)', r'_\1', clz.__name__).lower() + 's_'
    # tmp_dict = []
    # for s in data:
    # tmp_dict.append(s.items())
    return dict(map(lambda (key, value): (prefix + str(key), value), data.items()))


def convert_to_simplefields(clz, data):
    prefix = re.sub('(?!^)([A-Z]+)', r'_\1', clz.__name__).lower() + 's_'

    def get_field_key(prefix, key):
        if prefix in key:
            return key[len(prefix):]
        return key

    return dict(map(lambda (key, value): (get_field_key(prefix, key), value), data.items()))


properties = {
    "location": ["latitude", "longitude", "height", "dynamic_creation_date", "dynamic_ted",
                 "dynamic_uncertainty_weight", "dynamic_information_source", "dynamic_mechanism_obtained",
                 "dynamic_information_methodology"],
    "time": ["created", "edited", "deleted", "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
             "dynamic_information_source", "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    "duration": ["time_started", "time_ended", "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
                 "dynamic_information_source", "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    "address": ["street", "number", "apartment", "city", "locality", "country", "zip", "dynamic_creation_date",
                "dynamic_ted", "dynamic_uncertainty_weight", "dynamic_information_source", "dynamic_mechanism_obtained",
                "dynamic_information_methodology"],
    "current_location": ["latitude", "longitude", "height", "time", "dynamic_creation_date", "dynamic_ted",
                         "dynamic_uncertainty_weight", "dynamic_information_source", "dynamic_mechanism_obtained",
                         "dynamic_information_methodology"],
    "rating": ["value", "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
               "dynamic_information_source", "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    "mood": ["value", "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
             "dynamic_information_source", "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    "device": ["wireless_network_type", "wireless_channel_quality", "accelerometers", "cell_log", "sms_log", "call_log",
               "running_applications", "installed_applications", "screen_state", "battery_status",
               "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight", "dynamic_information_source",
               "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    "application": ["background_color", "format", "font", "color", "background", "text", "box", "classification",
                    "text_copy", "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
                    "dynamic_information_source", "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    "personalization": ["age_range", "country", "postal_code", "region", "town", "roaming", "opt_out", "carrier",
                        "handset", "user_ids", "device_id", "application_id", "device_type", "device_os", "gender",
                        "has_children", "ethnicity", "income", "household_size", "education", "interests",
                        "customer_tag",
                        "users_language", "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
                        "dynamic_information_source", "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    "community": ["list", "dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
                  "dynamic_information_source", "dynamic_mechanism_obtained", "dynamic_information_methodology"],
    # group
    # GroupFriend
    # Community
    # LocationVisit
}


def get_db_field(method, param):
    return method + "_" + param


class ContextPropertyResource(Resource):
    def get_list(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        db_fields = [get_db_field(kwargs['api_method'], x) for x in properties[kwargs['api_method']]]
        property_value = OpeniContext.objects.filter(objectid=kwargs['pk']).values(*db_fields)
        if len(property_value) > 0:
            base_bundle.data[kwargs['api_method']] = property_value[0]
        return self.create_response(request, base_bundle)

    def get_dynamic_list(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        dynamic_properties = ["dynamic_creation_date", "dynamic_ted", "dynamic_uncertainty_weight",
                              "dynamic_information_source", "dynamic_mechanism_obtained",
                              "dynamic_information_methodology"]
        db_fields = [get_db_field(kwargs['api_method'].replace("dynamic_", "", 1), x) for x in dynamic_properties]
        property_value = OpeniContext.objects.filter(objectid=kwargs['pk']).values(*db_fields)
        if len(property_value) > 0:
            base_bundle.data[kwargs['api_method']] = property_value[0]
        return self.create_response(request, base_bundle)

    def update(self, request, **kwargs):
        def populate(obj, api_method, request):
            for field in properties[api_method]:
                try:
                    val = request.GET[field]
                except MultiValueDictKeyError:
                    val = None
                obj.__dict__[get_db_field(api_method, field)] = val
            return obj

        context = OpeniContext()
        context.id = int(kwargs['pk'])
        context = populate(context, kwargs['api_method'], request)
        context = self.populate_dynamic_attributes(context)
        db_fields = [get_db_field(kwargs['api_method'], x) for x in properties[kwargs['api_method']]]
        context.save(update_fields=db_fields)
        return self.create_response(request, {})

    def populate_dynamic_attributes(self, context_bundle):
        for var in properties:
            is_empty = True
            ted = var+"_dynamic_ted"
            method = var+"_dynamic_information_methodology"
            source = var+"_dynamic_information_source"
            mechanism = var+"_dynamic_mechanism_obtained"
            creation_date = var+"_dynamic_creation_date"

            for cat_attr in properties[var]:
                if getattr(context_bundle, var+"_"+cat_attr) is not None:
                    is_empty = False
                    if "time" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "MT")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Direct")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "System")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Static")
                    elif "duration" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "MT")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Direct")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "System")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Derived")
                    elif "location" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "ST")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Direct")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "System")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Sensed")
                    elif "address" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "LT")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Indirect")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "Application")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Static")
                    elif "current_location" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "ST")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Indirect")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "System")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Sensed")
                    elif "rating" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "ST")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Indirect")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "Application")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Derived")
                    elif "mood" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "ST")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Indirect")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "Application")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Derived")
                    elif "device" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "F")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Direct")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "System")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Static")
                    elif "application" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "F")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Direct")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "Application")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Static")
                    elif "personalization" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "ST")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Indirect")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "Application")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Derived")
                    elif "community" == var:
                        if getattr(context_bundle, ted) is None:
                            setattr(context_bundle, ted, "MT")
                        if getattr(context_bundle, method) is None:
                            setattr(context_bundle, method, "Indirect")
                        if getattr(context_bundle, source) is None:
                            setattr(context_bundle, source, "Application")
                        if getattr(context_bundle, mechanism) is None:
                            setattr(context_bundle, mechanism, "Derived")

                    break
            if is_empty:
                setattr(context_bundle, var+"_dynamic_uncertainty_weight", Uncertainty.calculate_uncertainty(Uncertainty(), True, "", "", "", ""))
            else:
                setattr(context_bundle, var+"_dynamic_uncertainty_weight", Uncertainty.calculate_uncertainty(Uncertainty(), False,
                                                                                                      getattr(context_bundle, ted), getattr(context_bundle, source),
                                                                                                      getattr(context_bundle, mechanism), getattr(context_bundle, method)))
            setattr(context_bundle, creation_date, datetime.now())
        return context_bundle

class Uncertainty():
    def calculate_uncertainty(self, empty, dynamic_ted, dynamic_information_source, dynamic_mechanism_obtained,
                              dynamic_information_methodology):

        from random import randint
        import math

        mech_low_rand = float(randint(0, 30))/100
        mech_med_rand = float(randint(30, 60))/100
        mech_high_rand = float(randint(60, 100))/100

        source_low_rand = float(randint(0, 35))/100
        source_high_rand = float(randint(35, 100))/100

        method_low_rand = float(randint(0, 30))/100
        method_high_rand = float(randint(30, 100))/100

        ted_low_rand = float(randint(0, 25))/100
        ted_med_low_rand = float(randint(25, 50))/100
        ted_med_high_rand = float(randint(50, 75))/100
        ted_high_rand = float(randint(75, 100))/100

        uncertainty = 0

        if empty:
            return float(100)
        else:
            if dynamic_mechanism_obtained == 'Static':
                uncertainty += mech_low_rand * 50
            elif dynamic_mechanism_obtained == 'Sensed':
                uncertainty += mech_med_rand * 50
            elif dynamic_mechanism_obtained == 'Derived':
                uncertainty += mech_high_rand * 50
            else:
                uncertainty += 50;

            if dynamic_information_source == 'System':
                uncertainty += source_low_rand * 25
            elif dynamic_information_source == 'Application':
                uncertainty += source_high_rand * 25
            else:
                uncertainty += 25

            if dynamic_information_methodology == 'Direct':
                uncertainty += method_low_rand * 20
            elif dynamic_information_methodology == 'Indirect':
                uncertainty += method_high_rand * 20
            else:
                uncertainty += 20

            if dynamic_ted == 'F':
                uncertainty += ted_low_rand * 5
            elif dynamic_ted == 'FT':
                uncertainty += ted_med_low_rand * 5
            elif dynamic_ted == 'MT':
                uncertainty += ted_med_high_rand * 5
            elif dynamic_ted == 'ST':
                uncertainty += ted_high_rand * 5
            else:
                uncertainty += 5

            if uncertainty == 0:
                return float(100)
            else:
                return math.ceil(uncertainty)

class LocationVisitResource(Resource):
    def save_item(self, request, **kwargs):
        new_location_visit = json.loads(request.GET['data'])
        db_fields = convert_to_dbfields(LocationVisit, new_location_visit)
        try:
            lv = LocationVisit(**db_fields)
        except:
            raise BadRequest("invalid fields in json request")
        lv.context_id = int(kwargs['pk'])
        # lv.save()
        self.populate_dynamic_attributes(lv).save()
        return self.create_response(request, {})

    def update_item(self, request, **kwargs):
        if 'location_visits_id' not in request.GET:
            raise BadRequest("location_visits_id missing")
        updated_location_visit = json.loads(request.GET['data'])
        updated_db_fields = convert_to_dbfields(LocationVisit, updated_location_visit)
        location_visits = LocationVisit.objects.filter(id=int(request.GET['location_visits_id']))
        if len(location_visits) > 0:
            db_fields = get_fields(LocationVisit)
            for db_field in db_fields:
                if db_field in updated_db_fields:
                    location_visits[0].__dict__[db_field] = updated_db_fields[db_field]
            location_visits[0].save()
        else:
            raise BadRequest("location visit not found")
        self.populate_dynamic_attributes(location_visits).save()
        return self.create_response(request, {})

    def get_dynamic_list(self, request, **kwargs):
        db_fields = ["location_visits_dynamic_creation_date", "location_visits_dynamic_ted",
                     "location_visits_dynamic_uncertainty_weight",
                     "location_visits_dynamic_information_source", "location_visits_dynamic_mechanism_obtained",
                     "location_visits_dynamic_information_methodology"]
        base_bundle = self.build_bundle(request=request)
        objects = LocationVisit.objects.filter(context_id=kwargs['pk']).values(*db_fields)
        json_list = []
        if len(objects) > 0:
            for o in objects:
                lv_dict = convert_to_simplefields(LocationVisit, o)
                json_list.append(lv_dict)
            base_bundle.data["location_visits"] = json_list
        return self.create_response(request, base_bundle)

    def delete_item(self, request, **kwargs):
        LocationVisit.objects.filter(id=(request.GET['location_visits_id'])).delete()
        return self.create_response(request, {})

    def get_item(self, request, **kwargs):
        if 'location_visits_id' not in request.GET:
            raise BadRequest("location_visits_id missing")
        base_bundle = self.build_bundle(request=request)
        db_fields = get_fields(LocationVisit)
        objects = LocationVisit.objects.filter(context_id=1).values(*db_fields)
        if len(objects) > 0:
            lv_dict = convert_to_simplefields(LocationVisit, objects[0])
            base_bundle.data["location_visit"] = lv_dict
        return self.create_response(request, base_bundle)

    def get_list(self, request, **kwargs):
        db_fields = get_fields(LocationVisit)
        base_bundle = self.build_bundle(request=request)
        objects = LocationVisit.objects.filter(context_id=kwargs['pk']).values(*db_fields)
        json_list = []
        if len(objects) > 0:
            for o in objects:
                lv_dict = convert_to_simplefields(LocationVisit, o)
                json_list.append(lv_dict)
            base_bundle.data["location_visits"] = json_list
        return self.create_response(request, base_bundle)

    def populate_dynamic_attributes(self, lv):
        is_empty = True
        for attr, value in lv.__dict__.iteritems():
            if value is not None:
                is_empty = False
                if lv.location_visits_dynamic_ted is None:
                    lv.location_visits_dynamic_ted = "MT"
                if lv.location_visits_dynamic_information_methodology is None:
                    lv.location_visits_dynamic_information_methodology = "Indirect"
                if lv.location_visits_dynamic_information_source is None:
                    lv.location_visits_dynamic_information_source = "Application"
                if lv.location_visits_dynamic_mechanism_obtained is None:
                    lv.location_visits_dynamic_mechanism_obtained = "Derived"
                break

        lv.location_visits_dynamic_uncertainty_weight = Uncertainty.calculate_uncertainty(Uncertainty(), is_empty,
                                                                    lv.location_visits_dynamic_ted,
                                                                    lv.location_visits_dynamic_information_source,
                                                                    lv.location_visits_dynamic_mechanism_obtained,
                                                                    lv.location_visits_dynamic_information_methodology)
        lv.location_visits_dynamic_creation_date = datetime.now()
        return lv


class GroupResource(Resource):
    def get_item(self, request, **kwargs):
        fields = ["id", "group_name", "group_type"]
        base_bundle = self.build_bundle(request=request)
        groups = Group.objects.filter(context_id=int(kwargs['pk'])).prefetch_related("groupfriend_set")
        group_dicts = []
        for group in groups:
            group_dict = model_to_dict(group)
            group_dict = convert_to_simplefields(Group, group_dict)
            group_dict['group_friends'] = ValuesQuerySetToDict(group.groupfriend_set.values())
            group_dicts.append(group_dict)
        base_bundle.data['groups'] = group_dicts
        return self.create_response(request, base_bundle)

    def get_group_item(self, request, **kwargs):
        base_bundle = self.build_bundle(request=request)
        groups = Group.objects.filter(id=int(request.GET['group_id'])).prefetch_related("groupfriend_set")
        if len(groups) > 0:
            group_dict = model_to_dict(groups[0])
            group_dict['group_friends'] = ValuesQuerySetToDict(groups[0].groupfriend_set.values())
            base_bundle.data['group'] = group_dict
        return self.create_response(request, base_bundle)


    def get_dynamic_list(self, request, **kwargs):
        db_fields = ["group_dynamic_creation_date", "group_dynamic_ted", "group_dynamic_uncertainty_weight",
                     "group_dynamic_information_source", "group_dynamic_mechanism_obtained",
                     "group_dynamic_information_methodology"]
        base_bundle = self.build_bundle(request=request)
        objects = Group.objects.filter(context_id=kwargs['pk']).values(*db_fields)
        json_list = []
        if len(objects) > 0:
            for o in objects:
                lv_dict = convert_to_simplefields(LocationVisit, o)
                json_list.append(lv_dict)
            base_bundle.data["group"] = json_list
        return self.create_response(request, base_bundle)

    def update_item(self, request, **kwargs):
        groups = Group.objects.filter(id=int(request.GET['group_id'])).prefetch_related("groupfriend_set")
        base_bundle = self.build_bundle(request=request)
        if len(groups) > 0:
            group_update = json.loads(request.GET['data'])
            group = groups[0]
            if 'group_name' in group_update:
                group.group_name = group_update['group_name']
            if 'group_type' in group_update:
                group.group_type = group_update['group_type']
            # group.save()
            self.populate_dynamic_attributes(group).save()
            GroupFriend.objects.filter(group_id=int(request.GET['group_id'])).delete()
            group_friends = []
            for group_friend_updated in group_update['group_friends']:
                group_friend = GroupFriend(**group_friend_updated)
                group_friend.group_id = group.id
                group_friends.append(group_friend)
            if len(group_friends):
                GroupFriend.objects.bulk_create(group_friends)
        return self.create_response(request, base_bundle)

    def save_item(self, request, **kwargs):
        new_group = json.loads(request.GET['data'])
        new_group_friends = new_group.get('group_friends')
        if new_group_friends is not None:
            del new_group['group_friends']
        group = Group(**new_group)
        group.context_id = int(kwargs['pk'])
        self.populate_dynamic_attributes(group).save()
        group_friends = []
        if new_group_friends is not None:
            for new_group_friend in new_group_friends:
                group_friend = GroupFriend(**new_group_friend)
                group_friend.group_id = group.id
                group_friends.append(group_friend)
            GroupFriend.objects.bulk_create(group_friends)
        return self.create_response(request, {})

    def delete_item(self, request, **kwargs):
        Group.objects.filter(id=int(request.GET['group_id'])).delete()
        GroupFriend.objects.filter(group_id=request.GET['group_id']).delete()
        return self.create_response(request, {})

    def populate_dynamic_attributes(self, group):
        is_empty = True
        for attr, value in group.__dict__.iteritems():
            if value is not None:
                is_empty = False
                if group.group_dynamic_ted is None:
                    group.group_dynamic_ted = "MT"
                if group.group_dynamic_information_methodology is None:
                    group.group_dynamic_information_methodology = "Indirect"
                if group.group_dynamic_information_source is None:
                    group.group_dynamic_information_source = "Application"
                if group.group_dynamic_mechanism_obtained is None:
                    group.group_dynamic_mechanism_obtained = "Derived"
                break
        group.group_dynamic_uncertainty_weight = Uncertainty.calculate_uncertainty(Uncertainty(), is_empty,
                                                                            group.group_dynamic_ted,
                                                                            group.group_dynamic_information_source,
                                                                            group.group_dynamic_mechanism_obtained,
                                                                            group.group_dynamic_information_methodology)
        group.group_dynamic_creation_date = datetime.now()
        return group


class ContextResource(ModelResource):
    class Meta:
        queryset = OpeniContext.objects.all().prefetch_related("group_set", "locationvisit_set")
        location = fields.DictField()
        always_return_data = True
        list_allowed_methods = ['get', 'post']
        detail_allowed_methods = ['get', 'post', 'put', 'delete']
        # authentication = Authentication()
        # authorization = Authorization()
        excludes = ['id']
        # include_resource_uri = False

        filtering = {
            'id': ['exact']
        }

        resource_name = "Context"

        extra_actions = [
            {
                "name": "location",
                "http_method": "GET",
                "summary": "Retrieve context location of an object",
                "fields": {
                }
            },
            {
                "name": "dynamic_location",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of location of an object",
                "fields": {
                }
            },
            {
                "name": "location",
                "http_method": "PUT",
                "summary": "Update a context location",
                "fields": {
                    "latitude": {
                        "type": "string",
                        "required": False,
                        "description": "latitude of the location"
                    },
                    "longitude": {
                        "type": "string",
                        "required": False,
                        "description": "longitude of the location"
                    },
                    "height": {
                        "type": "string",
                        "required": False,
                        "description": "height of the location"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the location"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the location"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the location"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the location"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the location"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the location"
                    },
                }
            },
            {
                "name": "time",
                "http_method": "GET",
                "summary": "Retrieve context time of an object",
                "fields": {
                }
            },
            {
                "name": "dynamic_time",
                "http_method": "GET",
                "summary": "Retrieve Retrieve dynamic metadata of time of an object",
                "fields": {
                }
            },
            {
                "name": "time",
                "http_method": "PUT",
                "summary": "Update context time of an object",
                "fields": {
                    "created": {
                        "type": "string",
                        "required": False,
                        "description": "time of object creation"
                    },
                    "deleted": {
                        "type": "string",
                        "required": False,
                        "description": "time of object deletion"
                    },
                    "edited": {
                        "type": "string",
                        "required": False,
                        "description": "time of object update"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of tine"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of time"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of time"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of time"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of time"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of time"
                    },
                }
            },
            {
                "name": "duration",
                "http_method": "GET",
                "summary": "Retrieve context duration of an object",
                "fields": {
                }
            },
            {
                "name": "dynamic_duration",
                "http_method": "GET",
                "summary": "Retrieve dynamic context duration of an object",
                "fields": {
                }
            },
            {
                "name": "duration",
                "http_method": "PUT",
                "summary": "Update context duration of an object",
                "fields": {
                    "time_started": {
                        "type": "string",
                        "required": False,
                        "description": "the time the object started"
                    },
                    "time_ended": {
                        "type": "string",
                        "required": False,
                        "description": "the time the object ended"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the duration"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the duration"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the duration"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the duration"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the duration"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the duration"
                    },
                }
            },
            {
                "name": "address",
                "http_method": "GET",
                "summary": "Retrieve context location address",
                "fields": {
                }
            },
            {
                "name": "dynamic_address",
                "http_method": "GET",
                "summary": "Retrieve Retrieve dynamic metadata of address of an object",
                "fields": {
                }
            },
            {
                "name": "address",
                "http_method": "PUT",
                "summary": "Update context location address of an object",
                "fields": {
                    "street": {
                        "type": "string",
                        "required": False,
                        "description": "the context location street"
                    },
                    "number": {
                        "type": "string",
                        "required": False,
                        "description": "the context location street number"
                    },
                    "apartment": {
                        "type": "string",
                        "required": False,
                        "description": "the context location apartment"
                    },
                    "city": {
                        "type": "string",
                        "required": False,
                        "description": "the context location city"
                    },
                    "locality": {
                        "type": "string",
                        "required": False,
                        "description": "the context location locality"
                    },
                    "country": {
                        "type": "string",
                        "required": False,
                        "description": "the context location country"
                    },
                    "zip": {
                        "type": "string",
                        "required": False,
                        "description": "the context location zip code"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the address"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the address"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the address"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the address"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the address"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the address"
                    },
                }
            },
            {
                "name": "current_location",
                "http_method": "GET",
                "summary": "Retrieve context current location",
                "fields": {
                }
            },
            {
                "name": "dynamic_current_location",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of current location of an object",
                "fields": {
                }
            },
            {
                "name": "current_location",
                "http_method": "PUT",
                "summary": "Update context current location",
                "fields": {
                    "latitude": {
                        "type": "string",
                        "required": False,
                        "description": "latitude of the current location"
                    },
                    "longitude": {
                        "type": "string",
                        "required": False,
                        "description": "longitude of the current location"
                    },
                    "height": {
                        "type": "string",
                        "required": False,
                        "description": "height of the current location"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the current location"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the current location"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the current location"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the current location"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the current location"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the current location"
                    },
                }
            },
            {
                "name": "rating",
                "http_method": "GET",
                "summary": "Retrieve context object rating",
                "fields": {
                }
            },
            {
                "name": "dynamic_rating",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of rating of an object",
                "fields": {
                }
            },
            {
                "name": "rating",
                "http_method": "PUT",
                "summary": "Update context object rating",
                "fields": {
                    "value": {
                        "type": "string",
                        "required": False,
                        "description": "value of rating"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the rating"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the rating"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the rating"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the rating"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the rating"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the rating"
                    },
                }
            },
            {
                "name": "mood",
                "http_method": "GET",
                "summary": "Retrieve context object mood",
                "fields": {
                }
            },
            {
                "name": "dynamic_mood",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of mood of an object",
                "fields": {
                }
            },
            {
                "name": "mood",
                "http_method": "PUT",
                "summary": "Update context object mood",
                "fields": {
                    "value": {
                        "type": "string",
                        "required": False,
                        "description": "value of mood"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the mood"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the mood"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the mood"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the mood"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the mood"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the mood"
                    },
                }
            },
            {
                "name": "device",
                "http_method": "GET",
                "summary": "Retrieve context object device",
                "fields": {
                }
            },
            {
                "name": "dynamic_device",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of device of an object",
                "fields": {
                }
            },
            {
                "name": "device",
                "http_method": "PUT",
                "summary": "Update context object device",
                "fields": {
                    "wireless_network_type": {
                        "type": "string",
                        "required": False,
                        "description": "wireless network type e.g. 3G,LTE"
                    },
                    "wireless_channel_quality": {
                        "type": "string",
                        "required": False,
                        "description": "wireless channel quality (e.g. good,bad,excelent,very good)"
                    },
                    "cell_log": {
                        "type": "string",
                        "required": False,
                        "description": "list of device cell identifiers, in comma-separated list"
                    },
                    "sms_log": {
                        "type": "string",
                        "required": False,
                        "description": "sms recipients phones list, in comma-separated list"
                    },
                    "running_applications": {
                        "type": "string",
                        "required": False,
                        "description": "list of running applications, in comma-separated list"
                    },
                    "installed_applications": {
                        "type": "string",
                        "required": False,
                        "description": "list of installed applications, in comma-separated list"
                    },
                    "screen_state": {
                        "type": "string",
                        "required": False,
                        "description": "the screen state"
                    },
                    "battery_status": {
                        "type": "string",
                        "required": False,
                        "description": "the battery status (e.g. low, medium, full)"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the device"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the device"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the device"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the device"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the device"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the device"
                    },
                }
            },
            {
                "name": "application",
                "http_method": "GET",
                "summary": "Retrieve context object application",
                "fields": {
                }
            },
            {
                "name": "dynamic_application",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of application of an object",
                "fields": {
                }
            },
            {
                "name": "application",
                "http_method": "PUT",
                "summary": "Update context object application",
                "fields": {
                    "background_color": {
                        "type": "string",
                        "required": False,
                        "description": "application's background color"
                    },
                    "format": {
                        "type": "string",
                        "required": False,
                        "description": "application's background color"
                    },
                    "font": {
                        "type": "string",
                        "required": False,
                        "description": "application's background color"
                    },
                    "color": {
                        "type": "string",
                        "required": False,
                        "description": "application's  color"
                    },
                    "background": {
                        "type": "string",
                        "required": False,
                        "description": "application's background "
                    },
                    "text": {
                        "type": "string",
                        "required": False,
                        "description": "application's text"
                    },
                    "box": {
                        "type": "string",
                        "required": False,
                        "description": "application's box"
                    },
                    "classification": {
                        "type": "string",
                        "required": False,
                        "description": "application's classification"
                    },
                    "text_copy": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the app"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the app"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the app"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the app"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the app"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the app"
                    },
                }
            },
            {
                "name": "personalization",
                "http_method": "GET",
                "summary": "Retrieve context object personalization",
                "fields": {

                }
            },
            {
                "name": "dynamic_personalization",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of personalization of an object",
                "fields": {
                }
            },
            {
                "name": "personalization",
                "http_method": "PUT",
                "summary": "Update context object personalization",
                "fields": {
                    "age_range": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "country": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "postal_code": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "region": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "town": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "roaming": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "opt_out": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "carrier": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "handset": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "user_ids": {
                        "type": "string",
                        "required": False,
                        "description": "application's text copy"
                    },
                    "device_id": {
                        "type": "string",
                        "required": False,
                        "description": "device's UUID or UDID"
                    },
                    "application_id": {
                        "type": "string",
                        "required": False,
                        "description": "application id"
                    },
                    "device_type": {
                        "type": "string",
                        "required": False,
                        "description": "the device model e.g. Samsung S4"
                    },
                    "device_os": {
                        "type": "string",
                        "required": False,
                        "description": "the device operatin system e.g Android"
                    },
                    "gender": {
                        "type": "string",
                        "required": False,
                        "description": "gender e.g. any, male, female"
                    },
                    "has_children": {
                        "type": "string",
                        "required": False,
                        "description": ""
                    },
                    "ethnicity": {
                        "type": "string",
                        "required": False,
                        "description": "ethnicity"
                    },
                    "income": {
                        "type": "string",
                        "required": False,
                        "description": "ethnicity"
                    },
                    "household_size": {
                        "type": "string",
                        "required": False,
                        "description": "Any, Exactly 1 Exactly 2 Exactly 3 Exactly 4, 2 or fewer, 2 or more, 3 or more, 4 or more , 5 or more"
                    },
                    "education": {
                        "type": "string",
                        "required": False,
                        "description": "education"
                    },
                    "interests": {
                        "type": "string",
                        "required": False,
                        "description": "interests"
                    },
                    "customer_tag": {
                        "type": "string",
                        "required": False,
                        "description": "e.g. Any, Those who received, Those who interacted with For Past Campaigns, Those who interacted with For Launched Campaigns"
                    },
                    "users_language": {
                        "type": "string",
                        "required": False,
                        "description": "language iso code"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the personalization"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the personalization"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the personalization"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the personalization"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the personalization"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the personalization"
                    },
                }
            },
            {
                "name": "location_visits",
                "http_method": "GET",
                "summary": "Retrieve context location visits",
                "fields": {
                    "location_visits_id": {
                        "type": "string",
                        "required": True,
                        "description": "context location visits id"
                    },
                }
            },
            {
                "name": "dynamic_location_visits",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of location visits of an object",
                "fields": {
                }
            },
            {
                "name": "location_visits_item",
                "http_method": "GET",
                "summary": "Retrieve context location visits object",
                "fields": {
                    "location_visits_id": {
                        "type": "string",
                        "required": True,
                        "description": "context location visits id"
                    },
                }
            },
            {
                "name": "location_visits_item",
                "http_method": "PUT",
                "summary": "Update Context visit location",
                "fields": {
                    "location_visits_id": {
                        "type": "string",
                        "required": True,
                        "description": "context location visits id"
                    },
                    "data": {
                        "type": "array",
                        "required": True,
                        "description": "data value"
                    }
                }
            },
            {
                "name": "location_visits_item",
                "http_method": "POST",
                "summary": "create Context visit location",
                "fields": {
                    "data": {
                        "type": "array",
                        "required": True,
                        "description": "data value"
                    },
                }
            },
            {
                "name": "location_visits_item",
                "http_method": "DELETE",
                "summary": "delete context location visits object",
                "fields": {
                    "location_visits_id": {
                        "type": "string",
                        "required": True,
                        "description": "context location visits id"
                    },
                }
            },
            {
                "name": "groups",
                "http_method": "GET",
                "summary": "Retrieve context groups",
                "fields": {}
            },

            {
                "name": "groups",
                "http_method": "PUT",
                "summary": "Update context groups",
                "fields": {}
            },
            {
                "name": "groups_item",
                "http_method": "GET",
                "summary": "Retrieve a group",
                "fields": {
                    "group_id": {
                        "type": "string",
                        "required": True,
                        "description": "group id"
                    }
                }
            },
            {
                "name": "dynamic_groups_item",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of a group item of an object",
                "fields": {
                }
            },
            {
                "name": "groups_item",
                "http_method": "POST",
                "summary": "Create a group",
                "fields": {
                    "data": {
                        "type": "array",
                        "required": True,
                        "description": "data value"
                    },
                }
            },
            {
                "name": "groups_item",
                "http_method": "PUT",
                "summary": "Update a group",
                "fields": {
                    "group_id": {
                        "type": "string",
                        "required": True,
                        "description": "group id"
                    },
                    "data": {
                        "type": "array",
                        "required": True,
                        "description": "data value"
                    },
                }
            },
            {
                "name": "groups_item",
                "http_method": "DELETE",
                "summary": "delete a group",
                "fields": {
                    "group_id": {
                        "type": "string",
                        "required": True,
                        "description": "group id"
                    }
                }
            },
            {
                "name": "community",
                "http_method": "GET",
                "summary": "Retrieve community",
                "fields": {
                }
            },
            {
                "name": "dynamic_community",
                "http_method": "GET",
                "summary": "Retrieve dynamic metadata of community of an object",
                "fields": {
                }
            },
            {
                "name": "community",
                "http_method": "PUT",
                "summary": "Update community",
                "fields": {
                    "list": {
                        "type": "string",
                        "required": False,
                        "description": "value of mood"
                    },
                    "dynamic_creation_date": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic creation date of the community"
                    },
                    "dynamic_ted": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic TED of the community"
                    },
                    "dynamic_uncertainty_weight": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic uncertainty weight of the community"
                    },
                    "dynamic_information_source": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information source of the community"
                    },
                    "dynamic_mechanism_obtained": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic mechanism of the community"
                    },
                    "dynamic_information_methodology": {
                        "type": "string",
                        "required": False,
                        "description": "dynamic information methodology of the community"
                    },
                }
            },
        ]

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/location%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="location"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_location%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_location"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/time%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="time"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_time%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_time"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/duration%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="duration"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_duration%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_duration"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/address%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="address"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_address%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_address"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/current_location%s$" % (
                self._meta.resource_name, trailing_slash()), self.wrap_view('get_property'), name="current_location"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_current_location%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_current_location"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/rating%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="rating"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_rating%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_rating"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/mood%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="mood"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_mood%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_mood"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/device%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="device"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_device%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_device"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/application%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="application"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_application%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_application"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/personalization%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="personalization"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_personalization%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_personalization"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/location_visits%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="location_visits"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_location_visits%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_location_visits"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/location_visits_item%s$" % (
                self._meta.resource_name, trailing_slash()), self.wrap_view('get_property'),
                name="location_visits_item"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/community%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="community"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_community%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_community"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/groups%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="groups"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/groups_item%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="groups_item"),
            url(r"^(?P<resource_name>%s)/(?P<pk>\d+)/dynamic_groups_item%s$" % (
                self._meta.resource_name, trailing_slash()),
                self.wrap_view('get_property'), name="dynamic_groups_item"),


        ]

    def hydrate(self, bundle):
        def ungroupify(bundle):
            for property in properties:
                if property in bundle.data:
                    for val in properties[property]:
                        if val in bundle.data[property]:
                            db_field = get_db_field(property, val)
                            bundle.data[db_field] = bundle.data[property][val]
                            del bundle.data[property][val]
                    del bundle.data[property]
            return bundle

        bundle = ungroupify(bundle)
        return bundle

    def dehydrate(self, bundle):

        def groupify(bundle):
            for property in properties:
                bundle.data[property] = {}
                for val in properties[property]:
                    field = get_db_field(property, val)
                    bundle.data[property][val] = bundle.data[field]
                    del bundle.data[field]
            return bundle

        bundle = groupify(bundle)
        location_visits = bundle.obj.locationvisit_set.values()
        location_visits_list = ValuesQuerySetToDict(location_visits)
        lv_dic_list = []
        for location_visit in location_visits:
            lv_dict = convert_to_simplefields(LocationVisit, location_visit)
            lv_dic_list.append(lv_dict)

        groups = bundle.obj.group_set.values()
        groups_list = ValuesQuerySetToDict(groups)
        group_ids = []
        for group in groups_list:
            group['group_friends'] = []
            group_ids.append(group['id'])
        if len(group_ids) > 0:
            persons = GroupFriend.objects.filter(group__in=group_ids).order_by("group").values()
            persons_list = ValuesQuerySetToDict(persons)
            for group in groups_list:
                for person in persons_list:
                    if group['id'] == person['group_id']:
                        group['group_friends'].append(person)
        bundle.data['groups'] = groups_list
        bundle.data['location_visits'] = lv_dic_list
        return bundle

    # def obj_create(self, bundle,request = None,**kwargs):
    # return bundle

    def get_property(self, request, **kwargs):
        api_method = request.path.split("/")[-2]
        if api_method not in properties:
            if api_method == "location_visits":
                location_visit_resource = LocationVisitResource()
                return location_visit_resource.get_list(request, **kwargs)
            elif api_method == "location_visits_item":
                location_visit_resource = LocationVisitResource()
                if request.method == 'GET':
                    return location_visit_resource.get_item(request, **kwargs)
                elif request.method == 'POST':
                    return location_visit_resource.save_item(request, **kwargs)
                elif request.method == 'PUT':
                    return location_visit_resource.update_item(request, **kwargs)
                elif request.method == 'DELETE':
                    return location_visit_resource.delete_item(request, **kwargs)
            elif api_method == "groups":
                groups_resource = GroupResource()
                if request.method == 'GET':
                    return groups_resource.get_item(request, **kwargs)
                elif request.method == 'PUT':
                    return groups_resource.update(request, **kwargs)
            elif api_method == "groups_item":
                groups_resource = GroupResource()

                if request.method == 'GET':
                    return groups_resource.get_group_item(request, **kwargs)
                elif request.method == 'POST':
                    return groups_resource.save_item(request, **kwargs)
                elif request.method == 'DELETE':
                    return groups_resource.delete_item(request, **kwargs)
                elif request.method == 'PUT':
                    return groups_resource.update_item(request, **kwargs)

        kwargs["api_method"] = api_method
        child_resource = ContextPropertyResource()
        if "dynamic" in api_method:
            if "location_visits" in api_method:
                child_resource = LocationVisitResource()
            elif "groups_item" in api_method:
                child_resource = GroupResource()
            return child_resource.get_dynamic_list(request, **kwargs)
        if request.method == 'GET':
            return child_resource.get_list(request, **kwargs)
        elif request.method == 'PUT':
            return child_resource.update(request, **kwargs)






