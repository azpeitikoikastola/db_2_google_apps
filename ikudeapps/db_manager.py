# -*- coding: utf-8 -*-
import fdb


class DbConnect(object):

    def check_mandatory_fields(self, config):
        warning = []
        if not config.get('dsn'):
            warning.append('dsn')
        if not config.get('user'):
            warning.append('user')
        if not config.get('password'):
            warning.append('password')
        if warning:
            raise Warning('Honako eremuak beharrezkoak dira', ', '.join(warning))

    def __init__(self, config):
        dsn = config['dsn']
        user = config['user']
        password = config['password']
        self.db = fdb.connect(dsn=dsn, user=user, password=password)
        self.cr = self.db.cursor()

    def execute(self, sql, param):
        try:
            self.cr.execute(sql, param)
            try:
                return self.cr.fetchall()
            except:
                pass
        except Exception as e:
            print e.message
            self.db.rollback()

    def commit(self):
        return self.db.commit()

    def rollback(self):
        return self.db.rollback()