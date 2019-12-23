
import os
import sys

import django

# Initialize Django
print('Initializing Django...')
mydir = os.path.abspath(os.path.dirname(__file__))
sys.path.append(mydir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'history.settings')
django.setup()
print('Completed Django initialization.')

print('Importing required modules...')
from history import settings
from django.db import transaction
from django.contrib.auth.models import Permission, Group

from account import models as account
from occurrences import models as occurrences
from people import models as people
from places import models as places
from quotes import models as quotes
from sources import models as sources

print('Completed importing modules.')

try:
    print('Creating groups...')
    manager_group = Group()
    manager_group.name = 'Administrators'
    manager_group.save()
    for p in Permission.objects.all():
        manager_group.permissions.add(p)

    # customer group (customers have no permissions)
    contributor_group = Group()
    contributor_group.name = 'Contributors'
    contributor_group.save()
    print('Finished creating groups.')
except django.db.utils.IntegrityError:
    print('Groups already exist.')

# Delete existing data
occurrences.Occurrence.objects.all().delete()
occurrences.SourceReference.objects.all().delete()
people.Person.objects.all().delete()
places.City.objects.all().delete()
places.County.objects.all().delete()
places.State.objects.all().delete()
places.Country.objects.all().delete()
places.Continent.objects.all().delete()
places.Location.objects.all().delete()
quotes.Quote.objects.all().delete()
quotes.SourceReference.objects.all().delete()
sources.Source.objects.all().delete()
occurrences.Year.objects.all().delete()
account.User.objects.filter(is_superuser=False).delete()

# # Delete existing admins
# print('Deleting existing admins...')
# account.User.objects.filter(is_superuser=True).delete()
account.User.objects.filter(is_superuser=True, username__in=['jacob']).delete()

# Create admins
if not account.User.objects.filter(username='jacob', is_superuser=True).exists():
    print('Creating super admin...')
    u = account.User()
    u.is_active = True
    u.username = 'jacob'
    u.email = 'jacob.t.fredericksen@gmail.com'
    u.first_name = 'Jacob'
    u.last_name = 'Fredericksen'
    u.set_password('password')
    u.force_password_change = True if not settings.DEBUG else False
    u.is_superuser = True
    u.is_staff = True
    u.gender = 'M'
    u.save()
    print('Created superuser: %s' % u.get_full_name())

try:
    continent_names, continents = [
        'North America',
        'South America',
        'Antarctica',
        'Europe',
        'Asia',
        'Africa',
        'Oceania',
        'Zealandia',
    ], {}
    print('Adding continents...')
    for continent in continent_names:
        c = places.Continent.objects.create(name=continent)
        c.save()
        continents[continent] = c
except django.db.utils.IntegrityError:
    print('Continents already exist.')

countries = {}
try:
    country_names = (
        ('United States', 'North America'),
        ('Germany', 'Europe'),
        ('France', 'Europe'),
        ('Italy', 'Europe'),
        ('Japan', 'Asia'),
        ('New Zealand', 'Zealandia'),
    )
    print('Adding countries...')
    for country in country_names:
        country_name = country[0]
        c = places.Country.objects.create(name=country_name)
        c.save()
        countries[country_name] = c
except django.db.utils.IntegrityError:
    print('Continents already exist.')

try:
    state_names = (
        'New York',
        'Massachusetts',
        'Vermont',
        'Missouri',
        'Illinois',
        'Ohio',
        'Utah',
        'Texas'
    )
    print('Adding states...')
    for state in state_names:
        s = places.State.objects.create(name=state)
        s.location = countries['United States']
        s.save()
except django.db.utils.IntegrityError:
    print('States already exist.')


print('Creating people...')
# create the events
persons = {
    'Albert Einstein': {
        'dob': '1879-04-14',
        'dod': '1955-04-18'
    },
    'Joseph Smith': {
        'dob': '1805-12-23',
        'dod': '1844-06-27'
    },
    'Brigham Young': {
        'dob': '1801-06-01',
        'dod': '1877-08-29'
    },
    'Mark Twain': {
        'dob': '1835-11-30',
        'dod': '1910-04-21'
    },
    'Albert Schweitzer': {
        'dob': '1875-01-14',
        'dod': '1965-09-04',
    }
}
try:
    for person, details in persons.items():
        p = people.Person.objects.create(name=person, birth_date=details['dob'], death_date=details['dod'])
        p.description = 'aklsdlkfjs slkdfjlskdjflk lskdjflksdlf lskdjflksjdlkfj lksdjflskjdf lskdjflks.'
        p.save()
except django.db.utils.IntegrityError:
    print('States already exist.')

source_data = {
    'Bible Teaching and Religious Practice': {
        'text': 'Mark Twain, "Bible Teaching and Religious Practice," c. 1900.',
        'description': '...',
        'year': 1900,
    },
    'The Quest of the Historical Jesus': {
        'text': 'Albert Schweitzer, The Quest of the Historical Jesus, 1910, p. 25.',
        'description': '...',
        'year': 1906,
    },
}
source_objects = {}
for title, details in source_data.items():
    year = occurrences.Year.objects.create()
    year.ce = details['year']
    year.save()
    s = sources.Source.objects.create(text=details['text'], description=details['description'], year=year)
    s.description = 'aklsdlkfjs slkdfjlskdjflk lskdjflksdlf lskdjflksjdlkfj lksdjflskjdf lskdjflks.'
    s.save()
    source_objects[title] = s

for source in source_objects:
    occurrence = occurrences.Occurrence.objects.create(summary=f'Someone published {source}')


q = quotes.Quote.objects.create(text='''… there are some who are historians by the grace of God, who from their mother’s womb have an instinctive feeling for the real. They follow through all the intricacy and confusion of reported fact the pathway of reality, like a stream which, despite the rocks that encumber its course and the windings of its valley, finds its way inevitably to the sea. No erudition can supply the place of this historical instinct, but erudition sometimes serves a useful purpose, inasmuch as it produces in its possessors the pleasing belief that they are historians, and thus secures their services for the cause of history…. More often, however, the way in which erudition seeks to serve history is by suppressing historical discoveries as long as possible, and leading out into the field to oppose the one true view an army of possibilities. By arraying these in support of one another it finally imagines that it has created out of possibilities a living reality. This obstructive erudition is the special prerogative of theology, in which, even at the present day, a truly marvellous scholarship often serves only to blind the eyes to elementary truths, and to cause the artificial to be preferred to the natural. And this happens not only with those who deliberately shut their minds against new impressions, but also with those whose purpose is to go forward, and to whom their contemporaries look up as leaders…''')
qs = quotes.SourceReference.objects.create(quote=q, source=source_objects['The Quest of the Historical Jesus'], position=1)
q.sources.add = qs
q.save()

q = quotes.Quote.objects.create(text='''The Christian Bible is a drug store. Its contents remain the same; but the medical practice changes. For eighteen hundred years these changes were slight—scarcely noticeable. The practice was allopathic—allopathic in its rudest and crudest form. The dull and ignorant physician day and night, and all the days and all the nights, drenched his patient with vast and hideous doses of the most repulsive drugs to be found in the store’s stock; he bled him, cupped him, purged him, puked him, salivated him, never gave his system a chance to rally, nor nature a chance to help. He kept him religion sick for eighteen centuries, and allowed him not a well day during all that time. The stock in the store was made up of about equal portions of baleful and debilitating poisons, and healing and comforting medicines; but the practice of the time confined the physician to the use of the former; by consequence, he could only damage his patient, and that is what he did.''')
qs = quotes.SourceReference.objects.create(quote=q, source=source_objects['Bible Teaching and Religious Practice'], position=1)
q.sources.add = qs
q.save()

print('Initialization complete.')
