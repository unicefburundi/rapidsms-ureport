'''
Created on Mar 30, 2013

@author: asseym
'''
from django.test import TestCase
from django.contrib.sites.models import Site
from rapidsms.messages.incoming import IncomingMessage, OutgoingMessage
from rapidsms_httprouter.models import Message
from rapidsms.contrib.locations.models import Location, LocationType
import datetime
from rapidsms.models import Connection, Backend, Contact
from django.conf import settings
from script.models import Script, ScriptProgress, ScriptSession, ScriptStep
from rapidsms_httprouter.router import get_router
from django.core.management import call_command
from django.test.client import Client

class AutoRegTest(TestCase): #pragma: no cover
    fixtures = ['autoreg_data.json']
    # Model tests
    def setUp(self):
        
        if 'django.contrib.sites' in settings.INSTALLED_APPS:
            site_id = getattr(settings, 'SITE_ID', 2)
            Site.objects.get_or_create(pk=site_id, defaults={'domain':'ureport.com'})

        country = LocationType.objects.create(name='country', slug='country')
        province = LocationType.objects.create(name='province', slug='district')
        collin = LocationType.objects.create(name='collin', slug='collin')
        self.root_node = Location.objects.create(type=country, name='Burundi')
        self.bujumbura_province = Location.objects.create(type=province, name='Bujumbura')
        self.collin_collin = Location.objects.create(type=collin, name='kibenga')
        
    def fake_incoming(self, message, connection=None):
        if connection == None:
            connection = '8675309'
        c = Client()
        response = c.get(
        '/router/receive', \
        {\
          'backend' : 'test',\
          'password' : settings.ROUTER_PASSWORD,\
          'sender' : connection,\
          'message' : message\
          
        })

    def elapseTime(self, progress, seconds):
        """
        This hack mimics the progression of time, from the perspective of a linear test case,
        by actually *subtracting* from the value that's currently stored (usually datetime.datetime.now())
        """
        progress.set_time(progress.time - datetime.timedelta(seconds=seconds))
        try:
            session = ScriptSession.objects.get(connection=progress.connection, script__slug=progress.script.slug, end_time=None)
            session.start_time = session.start_time - datetime.timedelta(seconds=seconds)
            session.save()
        except ScriptSession.DoesNotExist:
            pass
        
    def testAutoregProgression(self):
        Script.objects.filter(slug='ureport_autoreg').update(enabled=True)
        print Script.objects.all()
        self.fake_incoming('join')
        script_prog = ScriptProgress.objects.get(connection__identity='8675309', script__slug='ureport_autoreg')
        self.elapseTime(script_prog, 61)
        call_command('check_script_progress', e=8, l=24)
        self.assertEquals(Message.objects.filter(direction='O').order_by('-pk')[0].text, Script.objects.get(slug='ureport_autoreg').steps.get(order=0).message)