# -*- coding: utf-8 -*-
from apiclient import errors


class Member(object):

    def __init__(self, data):
        self.email = data.get('email')
        self.role = data.get('role')
        self.type = data.get('type')

    @classmethod
    def create(cls, data):
        return Member(data)

    @classmethod
    def _create_member(cls, ac, data):
        try:
            new_group = ac.service.groups().insert(
                body=data).execute()
            return Member.create(new_group)
        except errors.HttpError as error:
            print 'An error occurred: %s' % error

    @classmethod
    def member_insert(cls, ac, user_email, group_key, role='MEMBER'):
        try:
            return ac.service.members().insert(body={'role': role, 'email': user_email}, groupKey=group_key).execute()
        except errors.HttpError as error:
            # Entity already exist
            if error.resp.get('status') == '409':
                return True
            elif error.resp.status == 403:
                raise Exception(error)
            else:
                print 'An error occurred: %s, user_email: %s' % (error.resp['status'], user_email)
                return False
#         {
#   "kind": "admin#directory#member",
#   "etag": etag,
#   "id": string,
#   "email": string,
#   "role": string,
#   "type": string
# }
