# -*- coding: utf-8 -*-

import xlrd
import getopt
import sys
import re
from group import Group
from member import Member
from system_object import SystemObject


class CalcImport(SystemObject):

    def __init__(self, file):
        super(CalcImport, self).__init__()
        self.file = file

    # TODO Hardcondea kendu
    def check_fields(self, sheet, ncols):
        res_fields = []
        fields = {
            'taldea': 'group',
            'izena': 'name',
            'izen-abizenak': 'name',
            'emaila': 'email',
            'emaila2': 'email2',
            'telefonoa': 'phone',
            'telefonoa2': 'phone2',
            'telefonoa3': 'phone3',
            'grupo': 'group',
            'nombre': 'name',
            'telefono': 'phone',
            'telefono2': 'phone2',
            'telefono3': 'phone3',
            'e-posta1': 'email',
            'e-posta2': 'email2'}
        for j in range(ncols - 1):
            name = sheet.cell_value(0, j)
            if not name:
                res_fields.append(False)
                continue
            name = name.lower()
            res = fields.get(name, False)
            assert res, "Zuzendu fitxategiaren goiburukoak. Onartutako eremuak: taldea, izena, emaila," \
                        " telefonoa, telefonoa2, telefonoa3" + sheet.cell_value(0, j) + str(j)
            res_fields.append(res)
        return res_fields

    def check_users(self, users):
        checked_users = []
        for user in users:
            if not(user.get('group') and user.get('name')):
                raise Warning("Taldea eta izena beharrezkoak dira", "Gutxienez batek esleitu gabe ditu: %s" % str(user))
            if self.check_email(user):
                checked_users.append(user)
        return checked_users

    def get_mapping(self):
        doc = xlrd.open_workbook(self.file)
        users = []
        user = {}
        checked_users = {}
        for sheet in doc.sheets():
            nrows = sheet.nrows
            ncols = sheet.ncols
            fields = self.check_fields(sheet, ncols)
            for i in range(1, nrows - 1):
                user = {}
                for j in range(ncols - 1):
                    if not sheet.cell_value(0, j):
                        continue
                    value = sheet.cell_value(i, j)
                    user.update({fields[j]: value})
                users.append(user)
        checked_users = self.check_users(users)
        return checked_users

    def check_email(self, user):
        if user.get('email'):
            if re.match(r"^[A-Za-z0-9\.\+_-]+@[A-Za-z0-9_-]+\.[a-zA-Z]*$", user['email']):
                # TODO idatzi loggerrien
                return True
            print "Bad spelled email: %s" % user['email']
        return False

    def get_groups(self, users):
        groups = set()
        for user in users:
            groups.add(user['group'])
        return groups


#TODO create orm
def update_db_info(db, columns, conditions):

    set_columns = '=?,'.join(columns.keys()) + '=?'
    set_conditions = '= ? and '.join(conditions.keys()) + '=?'
    check_update = "select nombre from familiar where %s" % set_conditions
    res = db.execute(check_update, conditions.values())
    if len(res)==1:
        sql = "update familiar set %s where %s" % (set_columns, set_conditions)
        db.execute(sql, columns.values()+conditions.values())
        db.db.commit()
    else:
        print 'name not unique %s' % conditions['name']
        return False

####### TODO create group class and move this method
def create_group_email(group_name, calc):
    if calc.force_group:
        return '@'.join([calc.force_group, calc.domain])
    suffix = calc.group_suffix
    prefix = calc.group_prefix
    pattern = re.compile('[\W_]+')
    name = ''.join([prefix.lower(), pattern.sub('', group_name).lower(), suffix.lower()])
    return '@'.join([name, calc.domain])

def main():
    calc = CalcImport(file)
    db = calc.db
    argv = sys.argv
    options, args = getopt.getopt(argv[1:], 'f:', [])
    file = ''
    for opt, value in options:
        if opt in ['-f']:
            file = value.strip()
    users = calc.get_mapping()
    groups = calc.get_groups(users)
    ac = calc.ac
    for group in groups:
        apps_group = create_group_email(group, calc)
        new_group = Group.create(ac, {'email':apps_group, 'name':group})
    for user in users:
        if not (user.get('email') or user.get('email2')):
            continue
        if user.get('email') and Member.members_insert(ac, user['email'], create_group_email(user['group'])):
            update_db_info(db, {'email': user['email']}, {'nombre': user['name']})
        if user.get('email2') and Member.members_insert(ac, user['email2'], create_group_email(user['group'])):
            update_db_info(db, {'email2': user['email2']}, 'nombre = %s' % user['name'])

if __name__ == "__main__":
    main()