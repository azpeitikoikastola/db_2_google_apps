# -*- coding: utf-8 -*-

import getopt
import logging
import sys
import time

from gappsconnect.group import Group
from gappsconnect.member import Member
from gappsconnect.orgunits import Orgunits
from gappsconnect.user import User
from gappsconnect.google_apps import AppsConnect
from db_manager import DbConnect

_logger = logging.getLogger(__name__)

SERVICE_NAME = 'admin'
SERVICE_VERSION = 'directory_v1'
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user',
          'https://www.googleapis.com/auth/admin.directory.group',
          'https://www.googleapis.com/auth/admin.directory.group.member',
          'https://www.googleapis.com/auth/admin.directory.orgunit']


class SystemObject(object):

    def __init__(self):
        config = {}
        execfile("config.conf", config)
        config['scopes'] = SCOPES
        config['service_name'] = SERVICE_NAME
        config['service_version'] = SERVICE_VERSION
        self.domain = config.get('domain')
        self.user_default_password = config.get('user_default_password')
        self.db = DbConnect(config)
        self.ac = AppsConnect(api_key=config['api_key'], scopes=SCOPES,
                              delegation_email=config['delegation_email'],
                              service_name=SERVICE_NAME,
                              service_version=SERVICE_VERSION)
        self.grade = config.get('grade')
        self.organization_unit_path = config.get('organization_unit_path')
        self.new_org_path = config.get('new_org_path')
        self.group_suffix = config.get('group_suffix', '')
        self.group_prefix = config.get('group_prefix', '')
        self.force_group = config.get('force_group')
        self.db_update_columns = config.get('db_update_columns')


def to_unicode(text):
    return text.decode('unicode-escape')


def _email_format(email):
    trans_table = dict(zip([ord(x) for x in u'áéíóúñÁÉÍÓÚÑ '],
                           u'aeiounAEIOUN'))
    trans_table.update(trans_table.fromkeys(map(ord, '  -'), None))
    unicode_email = email.decode('unicode-escape')
    return unicode_email.translate(trans_table).lower()


def _create_user_data(data):
    user = {
        u'name': {u'fullName': data['fullName'],
                  u'givenName': data['givenName'],
                  u'familyName': data['familyName'],
                  },
        u'primaryEmail': data['primaryEmail'],
        u'changePasswordAtNextLogin': True,
        u'password': data['password'],
        u'orgUnitPath': data['orgUnitPath']}
    return user


def _create_org_path(org_unit_path, new_org_path, year, grade_group):
    if new_org_path not in ['group', 'year', '']:
        raise Warning("Konfigurazio fitxategian new_org_path eremuak "
                      "'group', 'year' edo '' izan behar du")
    unit_path = org_unit_path if org_unit_path[-1] == '/' else org_unit_path + '/'
    if new_org_path == 'group':
        return unit_path + grade_group
    elif new_org_path == 'year':
        return unit_path + year
    else:
        return unit_path


# TODO lehen emailaren hardcodea kendu
def _format_data(ac, res, domain, def_pass, org_unit_path,
                 exist_orgunits, new_org_path):
    created_orgunits = []
    given_name = res[0].split()[0]
    family_name = res[1]
    full_name = res[2]
    year = str(res[3].year)
    grade_group = res[6]
    unit_path = _create_org_path(org_unit_path, new_org_path, year,
                                 grade_group)
    orgunit = to_unicode(unit_path)
    if orgunit not in exist_orgunits:
        created_orgunits = Orgunits.create_child_orgunits(ac, orgunit)
        exist_orgunits = []
    user_data = {
        'givenName': to_unicode(given_name),
        'familyName': to_unicode(family_name),
        'fullName': to_unicode(full_name),
        'orgUnitPath': orgunit in created_orgunits + exist_orgunits and orgunit or '/',
        'password': def_pass,
        'year': year,
        'primaryEmail': _email_format(
            "".join([given_name, family_name.split()[0],
                     year[-2:], "@", domain]))
                }
    user = _create_user_data(user_data)
    return user


def wait_until_group_creation(ac, email):
    for i in [1, 3, 5]:
        group = Group.get(ac, email)
        if not group:
            time.sleep(i)
            print 'Retrying...'
        else:
            print '{} is created and accessible'.format(group.email)
            return


def get_db_user_list(db, grade_list):
    if not isinstance(grade_list, tuple):
        grade_list = (grade_list,)

    sql = "select al.nombre0, al.apellidos, al.nombre, al.fechanac, al.id, " \
          "curso.descripcion, grupo.descripcion, al.email " \
          "from alumno al " \
          "inner join grupo on grupo.id = alumno.IDGRUPO " \
          "inner join curso on curso.id = alumno.IDCURSO " \
          "where al.idcurso in " \
          "(select curso.id from " \
          "cursoescolar inner join " \
                        "etapa on cursoescolar.id = etapa.idcursoescolar inner join " \
                        "ciclo on ciclo.idetapa = etapa.id inner join " \
                        "curso on curso.idciclo = ciclo.id " \
                        "where cursoescolar.cerrado='F' and curso.descripcion in (%s))" % ('?,' * len(grade_list))[:-1]
    result = db.execute(sql, grade_list)
    if not result:
        raise Warning("no results check that grades are correctly set")
    return result


def create_apps_group_add_members(sysconf):
    ac = sysconf.ac
    db = sysconf.db
    domain = sysconf.domain
    groups = {}
    result = get_db_user_list(db, sysconf.grade)
    for res in result:
        if res[7] and res[6]:
            if not groups.get(res[6]):
                # to sync the grade we need delete old group first
                email = _email_format('@'.join([res[6], domain]))
                Group.delete(ac, email)
                members_group = Group.create(ac, {'email': email})
                groups[res[6]] = members_group
                wait_until_group_creation(ac, email)
            Member.member_insert(ac, res[7], groups[res[6]].email)
        else:
            # logea eman
            pass


def create_apps_users_db_add_email(sysconf):
    ac = sysconf.ac
    db = sysconf.db
    domain = sysconf.domain
    exist_orgunits = []
    created_users_email = []
    result = get_db_user_list(db, sysconf.grade)
    for res in result:
        if res[0] and res[1] and res[3]:
            user = User.get(ac, res[7])
            if not user:
                user_data = _format_data(
                    ac, res, domain, sysconf.user_default_password,
                    sysconf.organization_unit_path, exist_orgunits,
                    sysconf.new_org_path)
                print unicode(user_data)
                try:
                    new_user = User.create(ac, user_data)
                    created_users_email.append(new_user.primaryEmail)
                    exist_orgunits.append(new_user.orgUnitPath)
                    try:
                        db.execute('update alumno set  email = ? where id = ?',
                                   [new_user.primaryEmail, res[4]])
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        print e.message
                except Exception as e:
                    print e.message
            else:
                print "User: %s already exist with email: %s" % (user.fullName, user.primaryEmail)
    return created_users_email


def sync_apps_users(sysconf, ignore=None):
    if not ignore:
        ignore=[]
    ac = sysconf.ac
    db = sysconf.db
    domain = sysconf.domain
    exist_orgunits = []
    result = get_db_user_list(db, sysconf.grade)
    for res in result:
        if res[0] and res[1] and res[3] and res[7] and res[7] not in ignore:
            user_data = _format_data(
                ac, res, domain, sysconf.user_default_password,
                sysconf.organization_unit_path, exist_orgunits,
                sysconf.new_org_path)
            print unicode(user_data)
            try:
                # without pop primaryEmail, the email can be overridden if the user name has a modification
                user_data.pop('primaryEmail')
                user_data.pop('changePasswordAtNextLogin')
                user_data.pop('password')
                new_user = User.update(ac, res[7], user_data)
                exist_orgunits.append(new_user.orgUnitPath)
            except Exception as e:
                print e.message


def main():
    sysconf = SystemObject()
    argv = sys.argv
    options, args = getopt.getopt(argv[1:], 'csg', [])
    created_users = []
    if not options:
        created_users = create_apps_users_db_add_email(sysconf)
        sync_apps_users(sysconf, ignore=created_users)
        create_apps_group_add_members(sysconf)
    else:
        for opt, value in options:
            if opt in ['-c']:
                created_users = create_apps_users_db_add_email(sysconf)
                break
        for opt, value in options:
            if opt in ['-s']:
                sync_apps_users(sysconf, ignore=created_users)
                break
        for opt, value in options:
            if opt in ['-g']:
                create_apps_group_add_members(sysconf)
                break

    #TODO clean groups and org units

if __name__ == "__main__":
    main()