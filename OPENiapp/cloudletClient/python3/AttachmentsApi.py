#!/usr/bin/env python
"""
WordAPI.py
Copyright 2014 Wordnik, Inc.

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

NOTE: This class is auto generated by the swagger code generator program. Do not edit the class manually.
"""
import sys
import os

from .models import *


class AttachmentsApi(object):

    def __init__(self, apiClient):
      self.apiClient = apiClient

    

    def uploadAttachment(self, cloudletId, additionalMetadata, file, **kwargs):
        """Creates an attachment to the JSON object

        Args:
            cloudletId, str: The id of the users cloudlet. (required)

            additionalMetadata, str: The file to upload (required)

            file, File: The file to upload (required)

            

        Returns: AttachmentStatus
        """

        allParams = ['cloudletId', 'additionalMetadata', 'file']

        params = locals()
        for (key, val) in params['kwargs'].items():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method uploadAttachment" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/attachments/{cloudletId}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        if ('cloudletId' in params):
            replacement = str(self.apiClient.toPathValue(params['cloudletId']))
            resourcePath = resourcePath.replace('{' + 'cloudletId' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'AttachmentStatus')
        return responseObject
        

        

    def getAttachmentCloudlet(self, cloudletId, attachmentId, meta, **kwargs):
        """Gets the attachment

        Args:
            cloudletId, str: The id of the users cloudlet. (required)

            attachmentId, str: The id of the binary data. (required)

            meta, bool: The binary data (required)

            

        Returns: AttachmentStatus
        """

        allParams = ['cloudletId', 'attachmentId', 'meta']

        params = locals()
        for (key, val) in params['kwargs'].items():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getAttachmentCloudlet" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/attachments/{cloudletId}/{attachmentId}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('meta' in params):
            queryParams['meta'] = self.apiClient.toPathValue(params['meta'])
        if ('cloudletId' in params):
            replacement = str(self.apiClient.toPathValue(params['cloudletId']))
            resourcePath = resourcePath.replace('{' + 'cloudletId' + '}',
                                                replacement)
        if ('attachmentId' in params):
            replacement = str(self.apiClient.toPathValue(params['attachmentId']))
            resourcePath = resourcePath.replace('{' + 'attachmentId' + '}',
                                                replacement)
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'AttachmentStatus')
        return responseObject
        

        

    




