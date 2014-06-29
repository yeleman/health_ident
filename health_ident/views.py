#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu

from __future__ import (unicode_literals, absolute_import,
                        division, print_function)

import smtplib

from django import forms
from django.shortcuts import render
from django.core.context_processors import csrf
from django.core import mail
from django.conf import settings
from django.template import loader, Context
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site

from health_ident import get_last_export
from health_ident.models import HealthEntity, Entity, AdministrativeEntity
from health_ident.storage import IdentEntity


class ContactForm(forms.Form):
    contact = forms.CharField(max_length=100, required=True,
                              label="Votre contact (email, téléphone)",
                              widget=forms.TextInput(attrs={'class': 'form-control',
                                                            'placeholder': "M. XXX, Chargé SIS à YYY. 77 77 77 77"}))
    message = forms.CharField(required=True,
                              widget=forms.Textarea(attrs={'class': 'form-control'}))
    entity_slug = forms.CharField(required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control',
                                                                'readonly': 'readonly'}))


def about(request, entity_slug=None):
    context = {"page": "about"}

    last_export_date = get_last_export()
    suffix = last_export_date.strftime("%Y-%m-%d")
    output_file = "all_entities-{}.json.bz2".format(suffix)
    output_sql = "all_entities-{}.sql".format(suffix)
    health_file = "health_entities-{}.csv".format(suffix)
    health_properties_file = "health_properties-{}.csv".format(suffix)
    health_history_file = "health_history-{}.csv".format(suffix)
    admin_file = "admin_entities-{}.csv".format(suffix)
    j2me_file = "j2me_csn-{0}.zip".format(suffix)

    context.update(({'last_export_date': last_export_date,
                     'admin_entities_file': admin_file,
                     'j2me_file': j2me_file,
                     'health_entities_file': health_file,
                     'health_properties_file': health_properties_file,
                     'health_history_file': health_history_file,
                     'all_entities_file': output_file,
                     'all_entities_sql': output_sql}))

    context.update({
        'nb_cscom_total': IdentEntity.find({'entity_type': 'health_center'}).count(),
        'nb_district_total': IdentEntity.find({'entity_type': 'health_district'}).count(),
        'nb_village_total': IdentEntity.find({'entity_type': 'vfq'}).count(),
        'nb_commune_total': IdentEntity.find({'entity_type': 'commune'}).count(),
        'nb_cercle_total': IdentEntity.find({'entity_type': 'cercle'}).count(),
        'nb_village_alone': IdentEntity.find({'entity_type': 'vfq', 'health_entity_code': ''}).count(),
        'nb_village_nocoord': IdentEntity.find({'entity_type': 'vfq', 'latitude': None}).count(),
        'nb_cscom_nocoord': IdentEntity.find({'entity_type': 'health_center', 'latitude': None}).count()
        })
    return render(request, "about.html", context)


def browser(request, entity_slug=None, **kwargs):
    context = {"page": "browser"}
    context.update(csrf(request))
    detailed_view = False

    if not entity_slug:
        entity_slug = 'mali'

    entity = IdentEntity.get_or_none(entity_slug)

    context.update({'entity': entity})

    if entity.entity_type == 'health_center':
        detailed_view = True

    if entity.entity_type == 'health_area':
        detailed_view = True

        context.update({'villages': IdentEntity.find({'health_entity_code': entity.code})})

    context.update({'detailed_view': detailed_view})

    initial = {
        'message': "Modification de {}/{}".format(entity.name, entity_slug),
        'entity_slug': entity.code}

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            body = "{}\n\n".format(form.cleaned_data.get('message'),
                                   form.cleaned_data.get('contact'))
            subject = "[IDENT] Correction pour {}".format(form.cleaned_data.get('entity_slug'))
            send_email(recipients=settings.RECIPIENTS,
                       message=body,
                       title=subject)
            form = ContactForm(initial=initial)

    else:
        form = ContactForm(initial=initial)
    context.update({'form': form})

    return render(request, kwargs.get('template_name', 'browser.html'), context)


def map(request):
    context = {"page": "map"}

    query = {'entity_type': 'health_center',
             'latitude': {'$ne': None},
             'longitude': {'$ne': None}}

    health_entities = IdentEntity.find(query)
    context.update({'health_entities': health_entities,
                    'nb_centers_total': IdentEntity.find({'entity_type': 'health_center'}).count(),
                    'nb_centers_nocoords': IdentEntity.find({'entity_type': 'health_center', 'latitude': None}).count()})

    return render(request, "map.html", context)


def send_email(recipients, message=None, template=None, context={}, \
               title=None, title_template=None, sender=None):
    """ forge and send an email message

        recipients: a list of or a string email address
        message: string or template name to build email body
        title: string or title_template to build email subject
        sender: string otherwise EMAIL_SENDER setting
        content: a dict to be used to render both templates

        returns: (success, message)
            success: a boolean if connecion went through
            message: an int number of email sent if success is True
                     else, an Exception """

    if not isinstance(recipients, (list, tuple)):
        recipients = [recipients]

    # remove empty emails from list
    # might happen everytime a user did not set email address.
    try:
        while True:
            recipients.remove("")
    except ValueError:
        pass

    # no need to continue if there's no recipients
    if len(recipients) == 0:
        return (False, ValueError(_("No Recipients for that message")))

    # no body text forbidden. most likely an error
    if not message and not template:
        return (False, ValueError(_("Unable to send empty email messages")))

    # build email body. rendered template has priority
    if template:
        email_msg = loader.get_template(template).render(Context(context))
    else:
        email_msg = message

    # if no title provided, use default one. empty title allowed
    if title == None and not title_template:
        email_subject = _("Message from %(site)s") \
                        % {'site': Site.objects.get_current().name}

    # build email subject. rendered template has priority
    if title_template:
        email_subject = loader.get_template(title_template) \
                              .render(Context(context))
    elif title != None:
        email_subject = title

    # title can't contain new line
    email_subject = email_subject.strip()

    # default sender from config
    if not sender:
        sender = settings.EMAIL_SENDER

    msgs = []
    for recipient in recipients:
        msgs.append((email_subject, email_msg, sender, [recipient]))

    try:
        mail.send_mass_mail(tuple(msgs), fail_silently=False)
        return (True, recipients.__len__())
    except smtplib.SMTPException as e:
        # log that error
        return (False, e)
