# -*- coding: utf-8 -*-


class Group(object):


    def __init__(self, email=None, name=None, **kwargs):
        self.email = email
        self.name = name

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