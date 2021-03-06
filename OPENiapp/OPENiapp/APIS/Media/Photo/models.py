from OPENiapp.APIS.models import LocationModel, TagsModel, GenericModel, BaseFileModel

__author__ = 'mpetyx'

from django.db import models



class OpeniPhoto(GenericModel):
    # id is missing because it is the default
    BaseFile = models.ForeignKey(BaseFileModel, blank=True, null=True)
    Location = models.ForeignKey(LocationModel, blank=True, null=True)
    Tags = models.ForeignKey(TagsModel, blank=True, null=True)
    width = models.TextField()
    height = models.TextField()
