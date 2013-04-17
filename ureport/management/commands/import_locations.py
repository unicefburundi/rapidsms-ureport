'''
Created on Apr 15, 2013

@author: asseym
'''

import xlrd
from optparse import OptionParser, make_option
import datetime

from django.core.management.base import BaseCommand
from rapidsms.contrib.locations.models import Location, Point

class Command(BaseCommand):


    option_list = BaseCommand.option_list + (
    make_option("-f", "--file", dest="path"),

    )
    
    def handle(self, **options):
        
        path = options["path"]
        workbook = xlrd.open_workbook(path)
        worksheets = workbook.sheet_names()
        
        for worksheet_name in worksheets:
            worksheet = workbook.sheet_by_name(worksheet_name)
            print worksheet