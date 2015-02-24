# -*- coding: utf-8 -*-

import sys
import getopt
import logging
from group import Group
from member import Member
from orgunits import Orgunits
from system_object import SystemObject
from user import User

_logger = logging.getLogger(__name__)

#### TODO create user class and modify methods
def to_unicode(text):
    return text.decode('unicode-escape')

def _email_format(email):
    trans_table = dict(zip([ord(x) for x in u'áéíóúñÁÉÍÓÚÑ'], u'aeiounAEIOUN'))
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
def _format_data(ac, res, domain, def_pass, org_unit_path, exist_orgunits, new_org_path):
    created_orgunits = []
    given_name = res[0].split()[0]
    family_name = res[1]
    full_name = res[2]
    year = str(res[3].year)
    grade_group = res[6]
    unit_path = _create_org_path(org_unit_path, new_org_path, year, grade_group)
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
        'primaryEmail': _email_format("".join([given_name, family_name.split()[0], year[-2:], "@", domain]))
                }
    user = _create_user_data(user_data)
    return user

def get_db_user_list(db, grade_list):
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
                        "where cursoescolar.cerrado='F' and curso.descripcion in %s)" % ("?" if isinstance(grade_list, tuple) and len(grade_list) > 1 else "%s%s%s" % ('(', '?', ')'))
    result = db.execute(sql, (grade_list,))
    if not result:
        raise Warning ("no results check that grades are correctly set")
    return result

def create_apps_group_add_members(sysconf):
    ac = sysconf.ac
    domain = sysconf.domain
    for grade in sysconf.grade:
        Group.create_group(ac, '@'.join([grade, domain]), grade)

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
                    ac, res, domain, sysconf.user_default_password, sysconf.organization_unit_path, exist_orgunits, sysconf.new_org_path)
                print unicode(user_data)
                try:
                    new_user = User.create(ac, user_data)
                    created_users_email.append(new_user.primaryEmail)
                    exist_orgunits.append(new_user.orgUnitPath)
                    #Member.members_insert(ac, new_user.primaryEmail, '@'.join([grade, domain]))
                    try:
                        db.execute('update alumno set  email = ? where id = ?', [new_user.primaryEmail, res[4]])
                        db.commit()
                    except Exception as e:
                        db.rollback()
                        print e.message
                except Exception as e:
                    #user = User.update(ac, user_data['primaryEmail'], user_data)
                    #Member.members_insert(ac, user.primaryEmail, '@'.join([grade, domain]))
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
                ac, res, domain, sysconf.user_default_password, sysconf.organization_unit_path, exist_orgunits, sysconf.new_org_path)
            print unicode(user_data)
            try:
                # without pop primaryEmail, the email can be overridden if the user name has a modification
                user_data.pop('primaryEmail')
                user_data.pop('changePasswordAtNextLogin')
                user_data.pop('password')
                new_user = User.update(ac, res[7], user_data)
                exist_orgunits.append(new_user.orgUnitPath)
                #Member.members_insert(ac, new_user.primaryEmail, '@'.join([grade, domain]))
            except Exception as e:
                #user = User.update(ac, user_data['primaryEmail'], user_data)
                #Member.members_insert(ac, user.primaryEmail, '@'.join([grade, domain]))
                print e.message




def main():
    sysconf = SystemObject()
    config = {}
    argv = sys.argv
    options, args = getopt.getopt(argv[1:], 'y:c', [])
    execfile("config.conf", config)
    #try:
    year = '%'
    course = '%'
    for opt, value in options:
        if opt in ['-y']:
            assert len(value) == 4, "urtea 4 digitotan"
            year = ''.join([value, '-%'])
        if opt in ['-c']:
            course = value.upper()
    # aurtengo grupuek ateatzeko grupo->curso->ciclo->etapa->curso-escolar
    #result = cr.execute("select nombre, fechanac
    #             from alumno
    #             where idgrupo in (select grupo.id
    #                               from cursoescolar inner join
    #                                    etapa on cursoescolar.id = etapa.idcursoescolar inner join
    #                                    ciclo on ciclo.idetapa = etapa.id inner join
    #                                    curso on curso.idciclo = ciclo.id inner join
    #                                    grupo on grupo.idcurso = curso.id
    #                               where cursoescolar.cerrado='F' and grupo.descripcion like ?)",['DBH-1%'])
    #result = db.execute("select nombre0,apellidos,fechanac "
    #                    "from alumno a inner join Curso c on a.idcurso=c.id "
    #                    "where c.descripcion like ? and fechanac like ?", [course, year])

    #TODO 4 funtziyo bat ikasliek sortzeko (sortutako ikaslien emailek bueltatzetxik) ta ikudean email kanpuen sortudan emaile idatzikoik beteta eon eo ez,
    #TODO bestie grupuek sortu ta memberrak gehitu(sortuta bazarek ez memberrak ez gehitu, bestela memberrak gehitu),
    #TODO  bestie sinkronizaziyue ikasliena(ikasletan updatiek emaile ibilita izenak, orgunitek... eta ) erabiltzailiek sortzekun antzekue createn partez update ibilita.
    #TODO azkena grupuen sikronizaziyue grupuen birsorketie(delete berriz sortu ta memberrak gehitu)
    #TODO kasu danetako beheko sqliek baliyo dula usteiat


    created_users = create_apps_users_db_add_email(sysconf)
    sync_apps_users(sysconf, ignore=created_users)
    #TODO
    #create_apps_group_add_members(sysconf)

if __name__ == "__main__":
    main()