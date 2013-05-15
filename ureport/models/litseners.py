#!/usr/bin/python
# -*- coding: utf-8 -*-

from rapidsms.models import Contact
from script.models import ScriptSession
from rapidsms_xforms.models import  XFormField
import datetime
from script.utils.handling import find_closest_match, find_best_response
from django.contrib.auth.models import  Group
from unregister.models import Blacklist
from ussd.models import Menu,StubScreen
import re
from models import AutoregGroupRules,EquatelLocation
from .utils import update_poll_results
from poll.models import ResponseCategory,Response,Poll
from rapidsms_httprouter.models import Message
#from rapidsms.router.db.models import Message
from django.conf import settings
from django.core.mail import send_mail
import difflib

def autoreg(**kwargs):
    connection = kwargs['connection']
    progress = kwargs['sender']
    if progress.script.slug in progress.script.slug in ['autoreg_en', 'autoreg_fr', 'autoreg_ki']:
        connection.contact = Contact.objects.create(name='Anonymous User')
        connection.save()
        session = ScriptSession.objects.filter(script=progress.script, connection=connection).order_by('-end_time')[0]
        script = progress.script
        reporter_group_poll = script.steps.get(order=1).poll
        reporter_reporting_location_poll = script.steps.get(order=2).poll
        reporter_colline_poll = script.steps.get(order=3).poll
        reporter_name_poll = script.steps.get(order=5).poll
        reporter_age_poll = script.steps.get(order=6).poll
        reporter_gender_poll = script.steps.get(order=7).poll
        contact = connection.contact
        word_dict=dict(AutoregGroupRules.objects.exclude(values=None).values_list('group__name','values'))
        name = find_best_response(session, reporter_name_poll)
        if name:
            contact.name = name[:100]

        contact.reporting_location = find_best_response(session, reporter_reporting_location_poll)

        age = find_best_response(session, reporter_age_poll)
        print age
        if age and age < 100:
            contact.birthdate = datetime.datetime.now() - datetime.timedelta(days=(365 * int(age)))

        gresps = session.responses.filter(response__poll=reporter_gender_poll, response__has_errors=False).order_by('-response__date')
        if gresps.count():
            gender = gresps[0].response
            if gender.categories.filter(category__name='male').count():
                contact.gender = 'M'
            elif gender.categories.filter(category__name='female').exists():
                contact.gender = 'F'

        colline = find_best_response(session, reporter_colline_poll)
        if colline:
            contact.colline = colline

        group_to_match = find_best_response(session, reporter_group_poll)
        gr_matched=False
        
        if group_to_match: #to avoid an attempt to None.split()
            try:
                for group_pk, word_list in word_dict.items():
                    if difflib.get_close_matches(group_to_match.lower(), word_list.split(',')):
                        contact.groups.add(Group.objects.get(name=group_pk))
                        gr_matched=True
            except AssertionError:
                pass
        default_group = None
        if progress.language:
            contact.language = progress.language
#        if Group.objects.filter(name='Other Reporters').count():
#            default_group = Group.objects.get(name='Other Reporters')
        try:
            default_group = Group.objects.get(name="Other Reporters")
            if group_to_match and not gr_matched:
                contact.groups.add(default_group)
        except Group.DoesNotExist:
            contact.groups.add(Group.objects.create(name="Other Reporters"))
    
#                for g in re.findall(r'\w+', group_to_match):
#                    if g:
#                        group = find_closest_match(str(g), Group.objects.exclude(name__in=["MP","delegate","CAO"]))
#                        if group:
#                            contact.groups.add(group)
#                            break
    
#                if default_group:
#                    contact.groups.add(default_group)
#            elif default_group:
#                contact.groups.add(default_group)

        if not contact.name:
            contact.name = 'Anonymous User'
        contact.save()

        total_ureporters = Contact.objects.exclude(connection__identity__in=Blacklist.objects.values_list('connection__identity')).count()
        if total_ureporters % getattr(settings, 'USER_MILESTONE', 500) == 0:
            recipients = getattr(settings, 'ADMINS', None)
            if recipients:
                recipients = [email for name, email in recipients]
            mgr = getattr(settings, 'MANAGERS', None)
            if mgr:
                for email in mgr:
                    recipients.append(email)
            send_mail("UReport now %d voices strong!" % total_ureporters, "%s (%s) was the %dth member to finish the sign-up.  Let's welcome them!" % (contact.name, connection.identity, total_ureporters), 'root@uganda.rapidsms.org', recipients, fail_silently=True)

def check_conn(sender, **kwargs):
    #delete bad connections
    c = kwargs['instance']
    if not c.identity.isdigit():
        c.delete()
        return True

def update_latest_poll(sender, **kwargs):

    poll=kwargs['instance']
    if poll.categories.filter(name__in=['yes','no']):
        try:
            xf=XFormField.objects.get(name='latest_poll')
            xf.question=poll.question
            xf.command="poll_"+str(poll.pk)
            xf.save()
            stub_screen=StubScreen.objects.get(slug='question_response')
            if poll.default_response:
                stub_screen.text=poll.default_response
                stub_screen.save()
            else:
                stub_screen.text="Thanks For Your Response."
                stub_screen.save()
            update_poll_results()
        except (XFormField.DoesNotExist,StubScreen.DoesNotExist):
            pass

        try:
            Menu.tree.rebuild()
        except:
            pass

def ussd_poll(sender, **kwargs):
    connection=sender.connection
    if not  sender.connection.contact:
        connection.contact = Contact.objects.create(name='Anonymous User')

        try:
            serial=sender.navigations.order_by('date')[1].response.rsplit("_")[0]
            connection.contact.reporting_location=EquatelLocation.objects.get(serial=serial).location
            connection.contact.save()
        except EquatelLocation.DoesNotExist:
            pass
        connection.save()
        equatel,created=Group.objects.get_or_create(name="equatel")
        connection.contact.groups.add(equatel)

    if sender.navigations.filter(screen__slug='weekly_poll').exists():
        field=XFormField.objects.get(name="latest_poll")
        nav=sender.navigations.filter(screen__slug='weekly_poll').latest('date')
        poll=Poll.objects.get(pk=int(field.command.rsplit('_')[1]))
        if poll.categories.filter(name__in=["yes","no"]):
            yes=poll.categories.get(name="yes")
            no=poll.categories.get(name='no')
            cats={'1':['yes',yes],'2':['no',no]}
            msg=Message.objects.create(connection=connection,text=cats[nav.response][0],direction="I")
            resp = Response.objects.create(poll=poll, message=msg, contact=connection.contact, date=nav.date)
            resp.categories.add(ResponseCategory.objects.create(response=resp, category=cats[nav.response][1]))
        #update results
    update_poll_results()

    if sender.navigations.filter(screen__slug='send_report'):
        Message.objects.create(connection=connection,text=sender.navigations.filter(screen__slug='send_report').latest('date').response,direction="I")


def add_to_poll(sender,**kwargs):
    try:
        contact=kwargs.get('instance').connection.contact
        poll=Poll.objects.get(name="blacklist")
        poll.contacts.add(contact)
    except:
        pass
