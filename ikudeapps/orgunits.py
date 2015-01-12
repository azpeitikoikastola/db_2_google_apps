# -*- coding: utf-8 -*-
from apiclient import errors


class Orgunits(object):

    def __init__(self, data):
        self.name = data.get('name')
        self.name = data.get('description')
        self.orgUnitPath = data.get('orgUnitPath')
        self.parentOrgUnitPath = data.get('parentOrgUnitPath')
        self.blockInheritance = data.get('blockInheritance')

    @classmethod
    def _create_orgunit(cls, data):
        return Orgunits(data)

    #api get method need the unit path without start slash
    @classmethod
    def remove_start_slash(cls, name):
        if isinstance(name, (str, unicode)):
            if name and name[0]=='/':
                return  name[1:]
            else:
                return name
        else:
            return map(lambda x: x[1:] if x and x[0]=='/' else x, name)

    @classmethod
    def create_child_orgunits(cls, ac, name):
        name = cls.remove_start_slash(name)
        if not isinstance(name, (list, tuple)):
            name = [name]
        unit_exist = []
        for unit in name:
            try:
                org_unit = ac.service.orgunits().get(orgUnitPath=unit, customerId='my_customer').execute()
                unit_exist.append(org_unit['orgUnitPath'])
            except errors.HttpError as error:
                user_input = raw_input("At least one child of %s organization unit doesn't exist. "
                                       "Do you want to create the whole structure? (Y/N): " % unit)
                while user_input not in ['Y', 'N']:
                    user_input = raw_input("Please type Y (yes) or N (no): ")
                if user_input == 'Y':
                    parent = ''
                    org_paths = unit.split('/')
                    for org_path in org_paths:
                        try:
                            org_unit = ac.service.orgunits().get(
                                orgUnitPath=parent and '/'.join([parent, org_path]) or org_path,
                                customerId='my_customer').execute()
                            parent = org_unit['orgUnitPath']
                            unit_exist.append(org_unit['orgUnitPath'])
                        except errors.HttpError as error:
                            try:
                                new_unit = ac.service.orgunits().insert(
                                    body={'name': org_path, 'parentOrgUnitPath': parent or '/'},
                                    customerId='my_customer').execute()
                                parent = new_unit['orgUnitPath']
                                unit_exist.append(new_unit['orgUnitPath'])
                            except errors.HttpError as error:
                                print error
        return unit_exist

    @classmethod
    def get_list(cls, ac, name):
        name = cls.remove_start_slash(name)
        try:
            return ac.service.orgunits().get(orgUnitPath=name, customerId='my_customer').execute()
        except errors.HttpError as error:
            cls.create_child_orgunits(ac, name)

    @classmethod
    def get(cls, ac, name):
        name = cls.remove_start_slash(name)
        if isinstance(name, (str, unicode)):
            try:
                orgunit = ac.service.orgunits().get(orgUnitPath=name, customerId='my_customer').execute()
                return cls._create_orgunit(orgunit)
            except errors.HttpError as error:
                print 'An error occurred: %s, organization unit: %s' % (error.resp['status'], name['name'])
        else:
            raise Warning("Name must be string. Use get_list method to get a list of organization units")

    @classmethod
    def create(cls, ac, data):
        try:
            orgunit = ac.service.orgunits().insert(body=data).execute()
            return cls._create_orgunit(orgunit)
        except errors.HttpError as error:
            print 'An error occurred: %s, organization unit: %s' % (error.resp['status'], data['name'])





#{
#  "kind": "admin#directory#orgUnit",
#  "etag": etag,
#  "name": string,
#  "description": string,
#  "orgUnitPath": string,
#  "parentOrgUnitPath": string,
#  "blockInheritance": boolean
#}
