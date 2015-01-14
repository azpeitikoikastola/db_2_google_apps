# -*- coding: utf-8 -*-
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
import httplib2
from apiclient import errors


class AppsConnect(object):

    def check_mandatory_fields(self, config):
        warning = []
        if not config.get('key_path'):
            warning.append('key_path')
        if not config.get('credentials_email'):
            warning.append('credentials_email')
        if not config.get('scope'):
            warning.append('scope')
        if not config.get('admin_email'):
            warning.append('admin_email')
        if not config.get('service_name'):
            warning.append('service_name')
        if not config.get('service_version'):
            warning.append('service_version')
        if warning:
            raise Warning('Honako eremuak beharrezkoak dira', ', '.join(warning))

    def __init__(self, config):
        self.check_mandatory_fields(config)
        with open(config['key_path'], 'r') as f:
            key = f.read()
        credentials = SignedJwtAssertionCredentials(config['credentials_email'],
                                                    key, scope=list(config['scope']),
                                                    sub=config['admin_email'])
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.service = build(config['service_name'], config['service_version'], http=http)






    def copy_group(self, old_key, new_email):
        page_token=True
        all_members = []
        while page_token:
            data = self.service.members().list({'pageToken': page_token}, groupKey=old_key).execute()
            all_members.extend(data.get('members'))
            page_token = data.get('nextPageToken')

        new_group = self.create_group(new_email)
        for member in all_members:
            self.members_insert(member['email'], new_email)
        return new_group

### Singleton#########################

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
