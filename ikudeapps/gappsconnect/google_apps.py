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

    def copy_group(self, old_key, new_email):
        page_token = True
        all_members = []
        while page_token:
            data = self.service.members().list({'pageToken': page_token},
                                               groupKey=old_key).execute()
            all_members.extend(data.get('members'))
            page_token = data.get('nextPageToken')

        new_group = self.create_group(new_email)
        for member in all_members:
            self.members_insert(member['email'], new_email)
        return new_group

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
