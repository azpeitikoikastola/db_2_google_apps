# -*- coding: utf-8 -*-


class Member(object):

    def __init__(self, email=None, role="MEMBER", **kwargs):
        self.email = email
        self.role = role
#         {
#   "kind": "admin#directory#member",
#   "etag": etag,
#   "id": string,
#   "email": string,
#   "role": string,
#   "type": string
# }
