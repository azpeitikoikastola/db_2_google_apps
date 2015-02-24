# -*- coding: utf-8 -*-
from apiclient import errors


class Group(object):


    def __init__(self, data):
        self.email = data.get('email')
        self.name = data.get('name')


    @classmethod
    def create(cls, ac, data):
        try:
            new_group = ac.service.groups().insert(
                body=data).execute()
            return Group.create(new_group)
        except errors.HttpError as error:
            print 'An error occurred: %s' % error

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