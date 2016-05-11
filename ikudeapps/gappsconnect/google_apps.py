# -*- coding: utf-8 -*-
from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
import httplib2


class AppsConnect(object):

    def check_mandatory_fields(self, api_key, scopes, delegation_email,
                               service_name, service_version):
        warning = []
        if not api_key:
            warning.append('api_key')
        if not scopes:
            warning.append('scopes')
        if not service_name:
            warning.append('service_name')
        if not service_version:
            warning.append('service_version')
        if not delegation_email:
            print Warning('"delegated_email" not supplied. May be mandatory')
        if warning:
            raise Warning('Mandatory arguments', ', '.join(warning))

    def __init__(self, api_key=None, scopes=None, delegation_email=None,
                 service_name=None, service_version=None):
        self.check_mandatory_fields(api_key, scopes, delegation_email,
                                    service_name, service_version)
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            api_key,
            scopes,
            )
        delegated_credentials = credentials.create_delegated(delegation_email)
        http = httplib2.Http()
        http = delegated_credentials.authorize(http)
        self.service = build(service_name, service_version, http=http)

# Singleton#########################

# class _Singleton(object):
#
#     def __init__(self):
#         # just for the sake of information
#         self.instance = "Instance at %d" % self.__hash__()
#
#
# _singleton = _Singleton()
#
# def Singleton(): return _singleton
