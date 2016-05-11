# -*- coding: utf-8 -*-
from apiclient import errors
from member import Member


class Group(object):


    def __init__(self, data):
        self.email = data.get('email')
        self.name = data.get('name')

    @classmethod
    def _create(cls, data):
        return Group(data)

    @classmethod
    def create(cls, ac, data):
        try:
            new_group = ac.service.groups().insert(
                body=data).execute()
            return Group._create(new_group)
        except errors.HttpError as error:
            print 'An error occurred: %s' % error

    @classmethod
    def get(cls, ac, key):
        try:
            group = ac.service.groups().get(
                groupKey=key).execute()
            return Group._create(group)
        except errors.HttpError as error:
            print 'An error occurred getting group: %s' % error

    @classmethod
    def delete(cls, ac, key):
        try:
            return ac.service.groups().delete(
                groupKey=key).execute()
        except errors.HttpError as error:
            if error.resp.status == 403:
                    raise Exception(error)
            print 'An error occurred: %s' % error

    def copy_group(self, ac, old_key, new_email):
        page_token = True
        all_members = []
        while page_token:
            data = ac.service.members().list({'pageToken': page_token},
                                               groupKey=old_key).execute()
            all_members.extend(data.get('members'))
            page_token = data.get('nextPageToken')

        new_group = self.create(ac, new_email)
        for member in all_members:
            Member.members_insert(ac, member['email'], new_email)
        return new_group

# {
#   "kind": "admin#directory#group",
#   "id": string,
#   "etag": etag,
#   "email": string,
#   "name": string,
#   "directMembersCount": long,
#   "description": string,
#   "adminCreated": boolean,
#   "aliases": [
#     string
#   ],
#   "nonEditableAliases": [
#     string
#   ]
# }