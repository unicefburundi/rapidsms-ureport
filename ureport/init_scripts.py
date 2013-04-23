#!/usr/bin/python
# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group
from ureport.models import AutoregGroupRules
from script.models import *
from eav.models import Attribute
from poll.models import Category, Rule
from poll.models import Translation
import re

def init_structures():
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
        site_id = getattr(settings, 'SITE_ID', 1)
        site = Site.objects.get_or_create(pk=site_id, defaults={'domain':'ureport.unicefburundi.org'})
        Poll.objects.all().delete()
        init_groups()
        init_eav_attributes(site[0])
        init_scripts(site[0])

def init_groups():
    groups = {
        'Red Cross': 'Red Cross,Redcross,Croix-Rouge,Croix Rouge',
        'Scouts': 'Scouts',
        'Guides': 'Guides',
        'Other Reporters': 'Other Reporters',
    }
    for g, aliases in groups.items():
        grp, _ = Group.objects.get_or_create(name=g)
        AutoregGroupRules.objects.get_or_create(group=grp, values=aliases)
        
        
def init_eav_attributes(site):
    if 'django.contrib.sites' in settings.INSTALLED_APPS:
#        site_id = getattr(settings, 'SITE_ID', 1)

#        site, created = Site.objects.get_or_create(pk=site_id, defaults={'domain':'ureport.unicefburundi.org'})
        eav_text_value = Attribute.objects.get_or_create(slug='poll_text_value', datatype=Attribute.TYPE_TEXT, site=Site.objects.get(id=site.id))
        eav_number_value = Attribute.objects.get_or_create(slug='poll_number_value', datatype=Attribute.TYPE_FLOAT, site=Site.objects.get(id=site.id))
        eav_location_value = Attribute.objects.get_or_create(slug='poll_location_value', datatype=Attribute.TYPE_OBJECT, site=Site.objects.get(id=site.id))
                
def init_scripts(site):
    #Message, Text, Rule, Start Offset, 'Retry Offset, Give up Offset, Number of Tries, 
    simple_scripts = {
        #English autoreg
	    'autoreg en':[     (False, "Welcome to Ureport Burundi, where you can SHARE and RECEIVE information about what is happening in your community. It’s FREE!", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_TEXT, 'reporter_group', "Do you belong to a volunteer organization? Please type ‘YES’ or ‘NO’ and the name of the organization ONLY.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_LOCATION, 'reporter_reporting_location', "Tell us where you'll be reporting from so we can work together to try resolve issues of your community! Reply with the name of your province ONLY.", ScriptStep.STRICT_MOVEON, 0, 86400, 0, 3,),
                           (Poll.TYPE_LOCATION, 'reporter_colline', "From which colline will you be reporting? Please respond ONLY with the name of your colline.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (False, "UReport is a FREE text messaging service sponsored by UNICEF and other partners.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_TEXT, 'reporter_name', "What is your name or nickname? User profiles help us make sense of the data that we receive.  Your name will not be revealed without your permission.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_NUMERIC, 'reporter_age', "What is your age?", ScriptStep.STRICT_MOVEON, 0, 86400, 0, 3,),
                           (Poll.TYPE_TEXT, 'reporter_gender', "Are you male or female? Type F for 'female' and M for 'male'", ScriptStep.WAIT_MOVEON, 0, False, False, 0, {"male":["m", "mal", "male", "ma", "mas", "masculin", "umugabo", "ga", "gabo", "gab"], "female": ["f", "fem", "female", "fe", "fém" "féminin", "fé", "umugore", "gore", "go", "gor"]}),
                           (False, "CONGRATULATIONS!! You are now  registered as a UReporter! Make a real difference with Ureport Burundi, Speak up and be heard! From UNICEF", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                     ],
        }
    script_translations = {
        #French autoreg
        'autoreg fr':[     (False, "Bienvenue dans Ureport/Burundi, ou tu peux PARTAGER et RECEVOIR l'information sur ce qui se passe dans ta communauté, C'est GRATUIT!", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_TEXT, 'reporter_group', "Appartiens-tu à une Organisation de volontaires? S'il te plaît réponds par oui ou non et le nom de l'organisation SEULEMENT", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_LOCATION, 'reporter_reporting_location', "Dis nous de quelle localité tu rapportes afin de travailler ensemble pour résoudre les défis de ta communauté! Réponds avec le nom de ta province!", ScriptStep.STRICT_MOVEON, 0, 86400, 0, 3,),
                           (Poll.TYPE_LOCATION, 'reporter_colline', "De quelle colline rapporteras-tu? S'il te plait réponds SEULEMENT avec le nom de ta colline. ", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (False, "UReport est un service GRATUIT de messagerie sponsorisée par l'UNICEF et d'autres partenaires.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_TEXT, 'reporter_name', "Quel est ton nom? Ton profil aide a donner un sens  aux données reçues . Ton nom ne sera pas révélé sans ta permission et tu peux utiliser un surnom.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_NUMERIC, 'reporter_age', "Quel est ton âge?", ScriptStep.STRICT_MOVEON, 0, 86400, 0, 3,),
                           (Poll.TYPE_TEXT, 'reporter_gender', "Es-tu de sexe masculin ou féminin? Écris F pour féminin et M pour masculin", ScriptStep.WAIT_MOVEON, 0, False, False, 0, {"male":["m", "mas", "masculin", "ma"], "female": ["f", "fem", "fém" "féminin", "fé"]}),
                           (False, "FELICITATIONS!! Tu es maintenant enregistré comme un Ureporter. Fais une vraie différence avec Ureport Burundi! Parles et soit écouté! De l'UNICEF", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                     ],
        #Kirundi autoreg
        'autoreg ki':[     (False, "Kaze muri Ureport/Burundi, aho ushobora gutanga no kuronka inkuru ku bibera mu karere uherereyemwo, Ni KU BUNTU!", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_TEXT, 'reporter_group', "Woba uri umunywanyi mw'ishirahamwe ry'abitanga? Ishura EGO canke OYA hamwe n'izina ry'iryo Shirahamwe GUSA.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_LOCATION, 'reporter_reporting_location', "Tubwire akarere utangiramwo inkuru, bidufashe gukorera hamwe gutorera inyishu ingorane zo mu karere kanyu! Ishura izina ry'intara yawe GUSA", ScriptStep.STRICT_MOVEON, 0, 86400, 0, 3,),
                           (Poll.TYPE_LOCATION, 'reporter_colline', "Ni uwuhe mutumba utangiramwo inkuru? Ishura izina ry'umutumba wawe GUSA.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (False, "Ureport Ni uburyo bwo kurungika ubutumwa ku buntu, bifashijwe n'intererano ya UNICEF n'ayandi mashiramwe.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_TEXT, 'reporter_name', "Tanga izina ryawe, ibikuranga bifasha guha insiguro inkuru turonse. Izina ryawe ntituritanga utaduhaye uruhusha kandi ushobora gutanga amatazirano", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                           (Poll.TYPE_NUMERIC, 'reporter_age', "Ufise imyaka ingahe?", ScriptStep.STRICT_MOVEON, 0, 86400, 0, 3,),
                           (Poll.TYPE_TEXT, 'reporter_gender', "Woba uri uw'igitsina Gore canke igitsina Gabo? Andika Go ari igitsina Gore Na Ga ari igitsina Gabo.", ScriptStep.WAIT_MOVEON, 0, False, False, 0, {"male":["umugabo", "ga", "gabo", "gab"], "female": ["umugore", "gore", "go", "gor"]}),
                           (False, "MURAKOZE!! Ubu uri umunywanyi WA Ureport. Gira ico uhinduye c'ukuri hamwe Na UReport Burundi. Vuga hama wumvirizwe! Kubwa UNICEF.", ScriptStep.WAIT_MOVEON, 0, False, False, 0,),
                     ],
    }

    user = User.objects.get_or_create(username='admin')[0]

    for script_name, polls in simple_scripts.items():
        Script.objects.filter(slug="%s"%script_name.lower().replace(' ', '_')).delete()
        script = Script.objects.create(slug="%s" % script_name.lower().replace(' ', '_'))
        script.name = "Ureport %s script" % script_name
        scriptname_parts = script_name.split(' ')
        script.save()
        created = True
        if created:
            script.sites.add(Site.objects.get_current())
            step = 0
            for poll_info in polls:
                if poll_info[0]:
                    Poll.objects.filter(name=poll_info[1]).delete()
                    poll = Poll.objects.create(user=user, type=poll_info[0], name='%s_%s'%(poll_info[1], scriptname_parts[1]), default_response='', question=poll_info[2])
                    poll.sites.add(Site.objects.get_current())
                    poll.save()
                    
                    if len(poll_info) > 8 and poll_info[8]:
                        for cat, rules in poll_info[8].items():
                            category, _ = Category.objects.get_or_create(name=cat, poll=poll)
                            regex = '%s%s%s'% ('^\s*(', '|'.join(rules), ')(\s|[^a-zA-Z]|$)')
                            rule, _ = Rule.objects.get_or_create(regex=regex, category=category, rule_type='r', rule_string='|'.join(rules))
                    if len(poll_info) > 9 and poll_info[9]:
                        poll.add_yesno_categories()
                    script.steps.add(\
                                ScriptStep.objects.get_or_create(
                                script=script,
                                poll=poll,
                                order=step,
                                rule=poll_info[3],
                                start_offset=poll_info[4],
                                retry_offset=poll_info[5],
                                giveup_offset=poll_info[6],
                                num_tries=poll_info[7],
                        )[0])
                else:
                    script.steps.add(\
                                ScriptStep.objects.get_or_create(
                                script=script,
                                message=poll_info[1],
                                order=step,
                                rule=poll_info[2],
                                start_offset=poll_info[3],
                                retry_offset=poll_info[4],
                                giveup_offset=poll_info[5],
                                num_tries=poll_info[6],
                        )[0])
                step = step + 1
                
    for script_name, polls in script_translations.items():
        Script.objects.filter(slug="%s"%script_name.lower().replace(' ', '_')).delete()
        script = Script.objects.create(slug="%s" % script_name.lower().replace(' ', '_'))
        script.name = "Ureport %s script" % script_name
        scriptname_parts = script_name.split(' ')
        script.save()
        created = True
        if created:
            script.sites.add(Site.objects.get_current())
            for en_step in ScriptStep.objects.filter(script__slug='autoreg_en'):
#                script.steps.add(en_step)
                if en_step.message:
                    script.steps.add(ScriptStep.objects.get_or_create(
                                    script=script,
                                    message=en_step.message,
                                    order=en_step.order,
                                    rule=en_step.rule,
                                    start_offset=en_step.start_offset,
                                    retry_offset=en_step.retry_offset,
                                    giveup_offset=en_step.giveup_offset,
                                    num_tries=en_step.num_tries,
                            )[0]
                        )
                else:
                    script.steps.add(ScriptStep.objects.get_or_create(
                                    script=script,
                                    poll=en_step.poll,
                                    order=en_step.order,
                                    rule=en_step.rule,
                                    start_offset=en_step.start_offset,
                                    retry_offset=en_step.retry_offset,
                                    giveup_offset=en_step.giveup_offset,
                                    num_tries=en_step.num_tries,
                            )[0]
                        )
            step = 0
            for poll_info in polls:
                if poll_info[0]:
                    translation, _ = Translation.objects.get_or_create(language=scriptname_parts[1], \
                                                field=Poll.objects.get(name='%s_en'% poll_info[1]).question, \
                                                value=poll_info[2])
                        
#                    if len(poll_info) > 8 and poll_info[8]:
#                        for cat, rules in poll_info[8].items():
#                            category = Category.objects.get(name=cat, poll=Poll.objects.get(name='%s_en'% poll_info[1]))
#                            rule = Rule.objects.get(category=category)
#                            new_regex = '%s%s|%s%s' % ('^\s*(', Rule.objects.get(category=category).rule_string.decode('utf-8'), '|'.join(rules), ')(\s|[^a-zA-Z]|$)')
#                            rule.regex = new_regex
#                            rule.rule_string = '%s|%s' % (Rule.objects.get(category=category).rule_string, '|'.join(rules))
#                            rule.save()
                else:
                    translation, _ = Translation.objects.get_or_create(language=scriptname_parts[1], \
                                                field=ScriptStep.objects.get(script__slug='autoreg_en', order=step).message, \
                                                value=poll_info[1])
                step = step + 1