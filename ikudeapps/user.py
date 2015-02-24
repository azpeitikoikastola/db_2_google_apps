# -*- coding: utf-8 -*-
from apiclient import errors

class User():

    def __init__(self, data):
        if data.get('name'):
            self.givenName = data['name'].get('givenName')
            self.familyName = data['name'].get('familyName')
            self.fullName = data['name'].get('fullName')
        self.primaryEmail = data.get('primaryEmail')
        self.orgUnitPath = data.get('orgUnitPath')
        self.password = data.get('password')
        self.changePasswordAtNextLogin = data.get('changePasswordAtNextLogin')

    #TODO create (address, organizations, phones...) class and add address array on create
    @classmethod
    def _create_user(cls, data):
        return User(data)

    @classmethod
    def create(cls, ac, data):
        try:
            user = ac.service.users().insert(body=data).execute()
            return cls._create_user(user)
        except errors.HttpError as error:
            print 'An error occurred: %s, user_email: %s' % (error.resp['status'], data['primaryEmail'])

    @classmethod
    def get(cls, ac, email):
        if email:
            try:
                user = ac.service.users().get(userKey=email).execute()
                return cls._create_user(user)
            except errors.HttpError as error:
                print 'An error occurred: %s, user_email: %s' % (error.resp['status'], email)

    @classmethod
    def update(cls, ac, email, data):
        try:
            user = ac.service.users().update(body=data, userKey=email).execute()
            return cls._create_user(user)
        except errors.HttpError as error:
            print 'An error occurred: %s, user_email: %s' % (error.resp['status'], data['primaryEmail'])
# {
#   "kind": "admin#directory#user",
#   "id": string,
#   "etag": etag,
#   "primaryEmail": string,
#   "name": {
#     "givenName": string,
#     "familyName": string,
#     "fullName": string
#   },
#   "isAdmin": boolean,
#   "isDelegatedAdmin": boolean,
#   "lastLoginTime": datetime,
#   "creationTime": datetime,
#   "deletionTime": datetime,
#   "agreedToTerms": boolean,
#   "password": string,
#   "hashFunction": string,
#   "suspended": boolean,
#   "suspensionReason": string,
#   "changePasswordAtNextLogin": boolean,
#   "ipWhitelisted": boolean,
#   "ims": [
#     {
#       "type": string,
#       "customType": string,
#       "protocol": string,
#       "customProtocol": string,
#       "im": string,
#       "primary": boolean
#     }
#   ],
#   "ims": string,
#   "emails": [
#     {
#       "address": string,
#       "type": string,
#       "customType": string,
#       "primary": boolean
#     }
#   ],
#   "emails": string,
#   "externalIds": [
#     {
#       "value": string,
#       "type": string,
#       "customType": string
#     }
#   ],
#   "externalIds": string,
#   "relations": [
#     {
#       "value": string,
#       "type": string,
#       "customType": string
#     }
#   ],
#   "relations": string,
#   "addresses": [
#     {
#       "type": string,
#       "customType": string,
#       "sourceIsStructured": boolean,
#       "formatted": string,
#       "poBox": string,
#       "extendedAddress": string,
#       "streetAddress": string,
#       "locality": string,
#       "region": string,
#       "postalCode": string,
#       "country": string,
#       "primary": boolean,
#       "countryCode": string
#     }
#   ],
#   "addresses": string,
#   "organizations": [
#     {
#       "name": string,
#       "title": string,
#       "primary": boolean,
#       "type": string,
#       "customType": string,
#       "department": string,
#       "symbol": string,
#       "location": string,
#       "description": string,
#       "domain": string,
#       "costCenter": string
#     }
#   ],
#   "organizations": string,
#   "phones": [
#     {
#       "value": string,
#       "primary": boolean,
#       "type": string,
#       "customType": string
#     }
#   ],
#   "phones": string,
#   "aliases": [
#     string
#   ],
#   "nonEditableAliases": [
#     string
#   ],
#   "customerId": string,
#   "orgUnitPath": string,
#   "isMailboxSetup": boolean,
#   "includeInGlobalAddressList": boolean,
#   "thumbnailPhotoUrl": string,
#   "customSchemas": {
#     (key): {
#       (key): (value)
#     }
#   }
# }