# -*- coding: utf-8 -*-
"""A set of request processors that return dictionaries to be merged into a
template context. Each function takes the request object as its only parameter
and returns a dictionary to add to the context.
"""
from rapidsms.models import Contact
from unregister.models import Blacklist
from poll.models import Poll
from django.conf import settings
from ureport.models import QuoteBox
from django.conf import settings


def voices(request):
    """
    a context processor that passes the total number of ureporters to all templates.
    """
    try:
        quote=QuoteBox.objects.latest()
    except QuoteBox.DoesNotExist:
        quote=None
    return {
        'total_ureporters':Contact.objects.exclude(connection__identity__in=Blacklist.objects.values_list('connection__identity')).count(),
        'polls':Poll.objects.exclude(contacts=None, start_date=None).exclude(pk__in=[297,296,349,350]).order_by('-start_date'),
       'deployment_id': getattr(settings, 'DEPLOYMENT_ID', 1),
       'quote':quote,
       'geoserver_url': getattr(settings, 'GEOSERVER_URL' , None),

        }



