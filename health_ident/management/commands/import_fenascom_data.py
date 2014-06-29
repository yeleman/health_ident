#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)
import os
import logging
import datetime

from optparse import make_option
from django.core.management.base import BaseCommand
from django.utils import timezone
from xlrd import open_workbook, xldate_as_tuple

from health_ident.storage import IdentEntity

logger = logging.getLogger(__name__)
date = 0
string = 1
numstring = 5
integer = 2
flo = 3
slug = 4

CSCOM = 'CSCOM'
ASACO = 'ASACO'
AIRE = 'AIRE'

NAMESPACE = 'fenascom'
NAMESPACE_RH = 'fenascom_rh'

def numstr(x):
    try:
        return str(int(x)).strip() if len(str(x)) else x
    except:
        return str(x)

def intt(x):
    try:
        return int(x)
    except:
        return str(x)

cleanup = {
    date: lambda x: datetime.date(*xldate_as_tuple(x, 0)[:3]).isoformat() if x != "" else None,
    string: lambda x: str(x).strip(),
    numstring: numstr,
    integer: intt,
    flo: lambda x: float(x),
    slug: lambda x: str(x).strip().upper() if len(x) else None
}

districts = {
    "TY60": "MACINA",
    "8R92": "MARKALA",
    "YF98": "SEGOU",
    "KZF8": "SAN",
    "84C0": "TOMINIAN",
    "A6T3": "BLA",
    "X952": "NIONO",
    "XN90": "BAROUELI",
}

ENTITY_MATRIX = {
    'NomASACO': ASACO,
    'DateOuverture': CSCOM,
    'NumeroTelephoneDTC': CSCOM,
    'DTC': CSCOM,
    'Commune': CSCOM,
    'PopulationTotale2014': AIRE,
    'DistanceDuCSRef': CSCOM,
    'NumeroRecepisse': ASACO,
    'NumeroTelephoneASACO': ASACO,
    'DureeMandatOrgane': ASACO,
    'DateCreation': ASACO,
    'LogistiqueMoyenDeplacement': CSCOM,
    'LogistiqueNombreMoyenDeplacement': CSCOM,
    'LogistiqueNombreBonEtat': CSCOM,
    'LogistiqueNombrePetrole': CSCOM,
    'LogistiqueNombreSolaire': CSCOM,
    'LogistiqueNombreCourant': CSCOM,
    'LogistiqueChaineFroidNom': CSCOM,
    'LogistiqueChaineFroidNombre': CSCOM,
    'LogistiqueChaineFroidNombreBonEtat': CSCOM,
}

cscom_matrix = {
    "MACINA": {"slug": 2, "NomASACO":  1, "DateOuverture": (5, date), "NumeroTelephoneDTC": (7, numstring), "Commune": 8, "PopulationTotale2014": (9, integer), "DistanceDuCSRef": (10, integer) },
    "MARKALA": {"slug": 2, "NomASACO":  1, "DateOuverture": (5, date), "NumeroTelephoneDTC": (7, numstring), "Commune": 8, "PopulationTotale2014": (9, integer), "DistanceDuCSRef": (10, integer)},
    "SEGOU": {"slug": 2, "NomASACO":  1, "DateOuverture": (5, date), "DTC": 6,  "NumeroTelephoneDTC": (7, numstring), "Commune": 8, "PopulationTotale2014": (9, integer), "DistanceDuCSRef": (10, integer)},
    "SAN": {"slug": 2, "NomASACO":  1, "DateOuverture": (5, date), "DTC": 6,  "NumeroTelephoneDTC": (7, numstring), "Commune": 8, "PopulationTotale2014": (9, integer), "DistanceDuCSRef": (10, integer)},
    "TOMINIAN": {"slug": 2, "NomASACO":  1, "DateOuverture": (5, date), "DTC": 6, "NumeroTelephoneDTC": (7, numstring), "Commune": 8, "PopulationTotale2014": (9, integer), "DistanceDuCSRef": (10, integer)},
    "BLA": {"slug": 1, "NomASACO":  2, "DTC": 5, "NumeroTelephoneDTC": (6, numstring), "Commune": 4, "PopulationTotale2014": (7, integer), "DistanceDuCSRef": (8, integer)},
    "NIONO": {"slug": 2, "NomASACO":  1, "DateOuverture": (5, date), "NumeroTelephoneDTC": (7, numstring), "Commune": 8, "PopulationTotale2014": (9, integer), "DistanceDuCSRef": (10, integer)},
    "BAROUELI": {"slug": 2, "NomASACO":  1, "DateOuverture": (5, date), "NumeroTelephoneDTC": (7, numstring), "Commune": 8, "PopulationTotale2014": (9, integer), "DistanceDuCSRef": (10, integer)},
}

asaco_matrix = {
    "MACINA": {"slug": 7, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
    "MARKALA": {"slug": 7, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
    "SEGOU": {"slug": 7, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
    "SAN": {"slug": 7, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
    "TOMINIAN": {"slug": 6, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
    "BLA": {"slug": 7, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
    "NIONO": {"slug": 7, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
    "BAROUELI": {"slug": 7, "NumeroRecepisse": 2, "NumeroTelephoneASACO": (3, numstring), "DureeMandatOrgane": (5, string), "DateCreation": (4, date), },
}

rh_matrix = {
    # "MACINA": {"Id": 0, "Nom": 1, "Prenom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
    # "MARKALA": {"Id": 0, "Nom": 1, "Prenom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
    # "SEGOU": {"Id": 0, "Nom": 1, "Prenom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
    # "SAN": {"Id": 0, "Nom": 1, "Prenom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
    # "TOMINIAN": {"Id": 0, "Nom": 1, "Prenom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
    # "BLA": {"Id": 0, "Nom": 1, "Prenom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
    # "NIONO": {"Id": 0, "Nom": 1, "Prenom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
    "BAROUELI": {"Id": 0, "Prenom": 1, "Nom": 2, "Poste": 3, "Sexe": 5, "Age": 6, },
}

logi_matrix = {
    "MACINA": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
               "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
               "LogistiqueChaineFroidNom": 8, "LogistiqueChaineFroidNombre": (9, integer), "LogistiqueChaineFroidNombreBonEtat": (10, integer)},
    "MARKALA": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
               "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
               "LogistiqueChaineFroidNom": 8, "LogistiqueChaineFroidNombre": (9, integer), "LogistiqueChaineFroidNombreBonEtat": (10, integer)},
    "SEGOU": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
               "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
               "LogistiqueChaineFroidNom": 8, "LogistiqueChaineFroidNombre": (9, integer), "LogistiqueChaineFroidNombreBonEtat": (10, string)},
    "SAN": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
            "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
            "LogistiqueChaineFroidNombre": (8, integer), "LogistiqueChaineFroidNombreBonEtat": (9, integer)},
    "TOMINIAN": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
            "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
            "LogistiqueChaineFroidNombre": (8, integer), "LogistiqueChaineFroidNombreBonEtat": (9, integer)},
    "BLA": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
            "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
            "LogistiqueChaineFroidNombre": (8, integer), "LogistiqueChaineFroidNombreBonEtat": (9, integer)},
    "NIONO": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
               "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
               "LogistiqueChaineFroidNom": 8, "LogistiqueChaineFroidNombre": (9, integer), "LogistiqueChaineFroidNombreBonEtat": (10, integer)},
    "BAROUELI": {"slug": 0, "LogistiqueMoyenDeplacement": 2, "LogistiqueNombreMoyenDeplacement": (3, integer), "LogistiqueNombreBonEtat": (4, integer),
               "LogistiqueNombrePetrole": (5, integer), "LogistiqueNombreSolaire": (6, integer), "LogistiqueNombreCourant": (7, integer),
               "LogistiqueChaineFroidNom": 8, "LogistiqueChaineFroidNombre": (9, integer), "LogistiqueChaineFroidNombreBonEtat": (10, integer)},
}

def update_metadata(slug, property_slug, pv):
    if pv is None:
        return
    # dval = pv.__class__ if not isinstance(pv, str) else "STR" #pv.decode('utf-8')
    try:
        dval = pv.encode('utf-8')
    except (UnicodeDecodeError, AttributeError):
        dval = "STR"
    print(u"{}/{}/{}".format(slug, property_slug, dval))

    dt = ENTITY_MATRIX.get(property_slug)
    if dt is AIRE:
        eslug = slug
    elif dt == CSCOM:
        eslug = slug[1:]
    elif dt == ASACO:
        eslug = "A{}".format(slug[1:])
    else:
        logger.error(dt)
        logger.error(property_slug)
        raise ValueError(property_slug)

    entity = IdentEntity.get_or_none(eslug)
    if entity is None:
        if slug == "CODE":
            return
        logger.debug(slug)
        logger.debug(eslug)
        raise ValueError("No match entity")

    if not NAMESPACE in entity.properties.keys():
        entity.properties.update({NAMESPACE: {}})
    entity.properties[NAMESPACE].update({property_slug: {'value': pv,
                                                         'modified_on': timezone.now()}})
    entity.save()


def update_rh(dist_slug, data):
    print(u"{}/{}".format(dist_slug, data))

    if not data.get('Id') or not data.get('Nom'):
        return

    eslug = "A{}".format(dist_slug)
    entity = IdentEntity.get_or_none(eslug)
    if entity is None:
        logger.debug(dist_slug)
        logger.debug(eslug)
        raise ValueError("No match entity RH")

    rhid = "rh_{}".format(int(float(data.pop('Id'))))

    if not NAMESPACE_RH in entity.properties.keys():
        entity.properties.update({NAMESPACE_RH: {}})
    entity.properties[NAMESPACE_RH].update({
        rhid: data})
    entity.save()


def getxl(sheet, row, col, cell_type=string):
    try:
        val = sheet.cell_value(int(row), int(col))
    except IndexError:
        print("Missing Data at {}x{}".format(row, col))
        return None
    return cleanup.get(cell_type)(val)


def property_import_cscom(folder):

    for district in districts.values():
        wb = open_workbook(
            os.path.join(folder, district, '{district}_CSCOM.xls'
                                            .format(district=district)))

        sheet_dicts = {'CSCOM': cscom_matrix.get(district),
                       'ASACO': asaco_matrix.get(district),
                       'RH_FELASCOM': rh_matrix.get(district)}
        print("-"*10, "DISTRICT: ", district, "-"*10)

        for sheet_name in sheet_dicts.keys():

            #DEBUG
            if sheet_name in ('CSCOM', 'ASACO'):
                continue

            try:
                print("*"*5, "sheet", sheet_name, "*"*5)
                sh = wb.sheet_by_name(sheet_name)
            except Exception as e:
                print(e, 'err'* 10)
                continue
            matrix_dict = sheet_dicts.get(sheet_name)
            for row in range(3, 30):
                data_rh = {}
                for property_slug in matrix_dict.keys():
                    if property_slug == 'slug':
                        continue
                    print("ROW/PROP", row, matrix_dict.get(property_slug))

                    if sheet_name == "RH_FELASCOM":
                        if (getxl(sh, row, matrix_dict.get("Prenom")) in (None, "")
                            and getxl(sh, row, matrix_dict.get("Nom")) in (None, "")):
                            break
                        else:
                            data_rh.update({property_slug: getxl(sh, row, matrix_dict.get(property_slug))})
                    else:
                        cscom_slug = getxl(sh, row, matrix_dict.get("slug"), slug)

                        if cscom_slug is None:
                            continue
                        psd = matrix_dict.get(property_slug)
                        if isinstance(psd, int):
                            ps = psd
                            ct = string
                        else:
                            ps, ct = psd
                        update_metadata(cscom_slug, property_slug, getxl(sh, row, ps, ct))
                update_rh(dict([(v,k) for k,v in districts.items()]).get(district),
                          data_rh) if sheet_name == "RH_FELASCOM" else None
        del(wb)
    print("End of the import CSCOM")



def import_logi_property(folder):
    for district in districts.values():
        print("-"*10, "DISTRICT: ", district, "-"*10)
        wb = open_workbook(
            os.path.join(folder, district, 'PEV_LOGIST_{district}.xlsx'
                                            .format(district=district)))
        sh = wb.sheet_by_name("logistique_chaine")
        logist_dict = logi_matrix.get(district)
        for row in range(5, 30):
            for property_slug in logist_dict:
                if property_slug == 'slug':
                    continue
                print("ROW/PROP", row, logist_dict.get(property_slug))
                cscom_slug = getxl(sh, row, logist_dict.get("slug"), slug)
                if cscom_slug is None:
                    continue
                psd = logist_dict.get(property_slug)
                if isinstance(psd, int):
                    ps = psd
                    ct = string
                else:
                    ps, ct = psd
                update_metadata(cscom_slug, property_slug, getxl(sh, row, ps, ct))
        del(wb)
    print("End of the import logistique")


class Command(BaseCommand):

    option_list = BaseCommand.option_list + (

        make_option('-p',
                    help='Path to root folder',
                    action='store',
                    dest='folder'),
    )

    def handle(self, *args, **options):

        folder = options.get('folder', None)
        if folder is None or not os.path.exists(folder):
            logger.error("Unable to access root folder")
            return

        logger.info("Importing CSCOM file data")
        property_import_cscom(folder)

        # logger.info("Importing LOGISTOCS file data")
        # import_logi_property(folder)
