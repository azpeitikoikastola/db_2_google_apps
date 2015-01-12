# -*- coding: utf-8 -*-
from db_manager import DbConnect
from google_apps import AppsConnect


class SystemObject(object):

    def __init__(self):
        config = {}
        execfile("config.conf", config)
        self.domain = config.get('domain')
        self.user_default_password = config.get('user_default_password')
        #self.db = DbConnect(config)
        self.ac = AppsConnect(config)
        self.grade = config.get('grade')
        self.organization_unit_path = config.get('organization_unit_path')
        self.group_suffix = config.get('group_suffix', '')
        self.group_prefix = config.get('group_prefix', '')
        self.force_group = config.get('force_group')
        self.db_update_columns = config.get('db_update_columns')

