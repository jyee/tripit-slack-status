import datetime
import os
from icalendar import Calendar
from urllib.request import urlopen, Request
from urllib.parse import quote, urlencode

# Read the calendar stream.
ical_url = os.environ.get('TRIPIT_ICAL_URL')
ical_reader = urlopen(ical_url)
ical = ical_reader.read()

# Setup data.
current_location = ''
current_location_date = datetime.date.today()
next_location = ''
next_location_date = datetime.date.today()
today = datetime.date.today()

# Parse the calendar stream.
cal = Calendar.from_ical(ical)
for event in cal.walk('vevent'):
    dtstart = event.get('dtstart').dt
    if isinstance(dtstart, datetime.date) and not isinstance(dtstart, datetime.datetime):
        current_location = next_location
        current_location_date = next_location_date
        next_location = event.get('location')
        next_location_date = dtstart
        if next_location_date > today:
            break;

status = '{c.month}/{c.day}: {cloc} .. {n.month}/{n.day}: {nloc}'.format(c=current_location_date, cloc=current_location, n=next_location_date, nloc=next_location)
emoji = os.environ.get('SLACK_STATUS_EMOJI') or ''

slack_url = 'https://slack.com/api/users.profile.set'
slack_profile = '{"status_text":"' + status + '", "status_emoji": "' + emoji + '"}'
slack_token = os.environ.get('SLACK_API_TOKEN')

post_data = {'token': slack_token, 'profile': slack_profile}
req = Request(slack_url, urlencode(post_data).encode())
resp = urlopen(req)
if resp.status == 200:
    print('Status updated: ' + status)
else:
    print(resp.read())
