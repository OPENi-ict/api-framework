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


class CloudletsApi(object):

    def __init__(self, apiClient):
      self.apiClient = apiClient

    

    def createCloudlet(self, body, **kwargs):
        """Creates a Cloudlet

        Args:
            body, OPENiCloudlet: The Cloudlet data (required)

            

        Returns: CloudletResponse
        """

        allParams = ['body']

        params = locals()
        for (key, val) in params['kwargs'].items():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method createCloudlet" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/cloudlets'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'POST'

        queryParams = {}
        headerParams = {}

        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'CloudletResponse')
        return responseObject
        

        

    def deleteCloudletById(self, cloudletId, **kwargs):
        """DELETE Cloudlet by Id

        Args:
            cloudletId, str: The id of the Cloudlet that is to be deleted. (required)

            

        Returns: CloudletResponse
        """

        allParams = ['cloudletId']

        params = locals()
        for (key, val) in params['kwargs'].items():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method deleteCloudletById" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/cloudlets/{cloudletId}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'DELETE'

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

        responseObject = self.apiClient.deserialize(response, 'CloudletResponse')
        return responseObject
        

        

    def exportCloudletById(self, cloudletId, **kwargs):
        """Export Cloudlet data.

        Args:
            cloudletId, str: The id of the Cloudlet that is to be exported. (required)

            

        Returns: OPENiCloudlet
        """

        allParams = ['cloudletId']

        params = locals()
        for (key, val) in params['kwargs'].items():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method exportCloudletById" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/cloudlets/{cloudletId}'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

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

        responseObject = self.apiClient.deserialize(response, 'OPENiCloudlet')
        return responseObject
        

        

    def getCloudlets(self, **kwargs):
        """Retrieves all Cloudlets on the platform.

        Args:
            skip, int: Pagination feature, the amount of objects to skip. (optional)

            limit, int: The amount of objects to return. (optional)

            id_only, bool: If true returns an array of object ids instead of the full objects. (optional)

            

        Returns: Array[OPENiCloudlet]
        """

        allParams = ['skip', 'limit', 'id_only']

        params = locals()
        for (key, val) in params['kwargs'].items():
            if key not in allParams:
                raise TypeError("Got an unexpected keyword argument '%s' to method getCloudlets" % key)
            params[key] = val
        del params['kwargs']

        resourcePath = '/cloudlets'
        resourcePath = resourcePath.replace('{format}', 'json')
        method = 'GET'

        queryParams = {}
        headerParams = {}

        if ('skip' in params):
            queryParams['skip'] = self.apiClient.toPathValue(params['skip'])
        if ('limit' in params):
            queryParams['limit'] = self.apiClient.toPathValue(params['limit'])
        if ('id_only' in params):
            queryParams['id_only'] = self.apiClient.toPathValue(params['id_only'])
        postData = (params['body'] if 'body' in params else None)

        response = self.apiClient.callAPI(resourcePath, method, queryParams,
                                          postData, headerParams)

        if not response:
            return None

        responseObject = self.apiClient.deserialize(response, 'Array[OPENiCloudlet]')
        return responseObject
        

        

    




