# -*- coding: utf-8 -*-

import sys
import getopt
import logging
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

# TODO orgUnitPath to config file
def _create_user_data(data):
    user = {
        u'name': {u'fullName': data['fullName'],
                  u'givenName': data['givenName'],
                  u'familyName': data['familyName'],
                  },
        u'primaryEmail': data['primaryEmail'],
        u'changePasswordAtNextLogin': True,
        u'password': data['password'],
        u'orgUnitPath':data['orgUnitPath']}
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
def _format_data(ac, res, domain, def_pass, org_unit_path, new_org_path):
    given_name = res[0]
    family_name = res[1]
    full_name = res[2]
    year = str(res[3].year)
    grade_group = res[6]
    unit_path = _create_org_path(org_unit_path, new_org_path, year, grade_group)
    orgunit = to_unicode(unit_path)
    exits_orgunits = Orgunits.create_child_orgunits(ac, orgunit)
    user_data = {
        'givenName': to_unicode(given_name),
        'familyName': to_unicode(family_name),
        'fullName': to_unicode(full_name),
        'orgUnitPath': orgunit in exits_orgunits and orgunit or '/',
        'password': def_pass,
        'year': year,
        'primaryEmail': _email_format("".join([given_name, family_name.split()[0], year[-2:], "@", domain]))
                }
    user = _create_user_data(user_data)
    return user





def main():
    sysconf = SystemObject()
    config = {}
    argv = sys.argv
    options, args = getopt.getopt(argv[1:], 'y:c', [])
    execfile("config.conf", config)
    domain = sysconf.domain
    user_default_password = sysconf.user_default_password
    org_unit_path = sysconf.organization_unit_path
    grade = sysconf.grade
    #try:
    db = sysconf.db
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
    for gr in grade:
        result = db.execute("select al.nombre0, al.apellidos, al.nombre, al.fechanac, al.id, "
                            "curso.descripcion, grupo.descripcion "
                            "from alumno al "
                            "inner join grupo on grupo.id = alumno.IDGRUPO "
                            "inner join curso on curso.id = alumno.IDCURSO "
                            "where al.idcurso in "
                            "(select curso.id from "
                            "cursoescolar inner join "
                            "etapa on cursoescolar.id = etapa.idcursoescolar inner join "
                            "ciclo on ciclo.idetapa = etapa.id inner join "
                            "curso on curso.idciclo = ciclo.id "
                            "where cursoescolar.cerrado='F' and curso.descripcion = ?)", [gr])

        #except Exception as e:
            #_logger.error('db error')
         #   print e.message
        #try:
        if not result:
            print "no result for the grade: %s" % gr
        exist_orgunits = []
        for res in result:
            if res[0] and res[1]:
                user_data = _format_data(res, domain, user_default_password, org_unit_path, exist_orgunits)
                print unicode(user_data)
                try:
                    new_user = User.create(sysconf.ac, user_data)
                    exist_orgunits.append(new_user.orgUnitPath)
                except Exception as e:
                    print e.message

                try:
                    db.execute('update alumno set  email = ? where id = ?', [new_user.primaryEmail, res[4]])
                    db.commit()
                except Exception as e:
                    db.rollback()
                    print e.message

        #except Exception as e:
         #   print e.message
            #_logger.error('Apps connection error')

if __name__ == "__main__":
    main()