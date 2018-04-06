import datetime
import os
from icalendar import Calendar
from urllib.request import urlopen, Request
from urllib.parse import urlencode

# Read the calendar stream.
ical_url = os.environ.get('TRIPIT_ICAL_URL')
ical_reader = urlopen(ical_url)
ical = ical_reader.read()

# Setup data.
today = datetime.date.today()
current_location_start = today
current_location = os.environ.get('TRIPIT_HOME')
next_location = os.environ.get('TRIPIT_HOME')

# Parse the calendar stream.
cal = Calendar.from_ical(ical)
for event in cal.walk('vevent'):
    dtstart = event.get('dtstart').dt
    dtend = event.get('dtend').dt
    location = event.get('location')
    # Trips only have dates, not times.
    if isinstance(dtstart, datetime.date) and not isinstance(dtstart, datetime.datetime):
        # If the trip has ended, ignore it.
        if today > dtend:
            continue;

        # If we're in the middle of a trip, set it as current.
        if dtstart <= today and today < dtend:
            current_location = location
            current_location_start = dtstart
            current_location_end = dtend

        # If we're seeing a future event
        if dtstart > today:
            # If coming from home, this is the next trip.
            if current_location == os.environ.get('TRIPIT_HOME'):
                next_location = location
                next_location_start = dtstart
            # If coming from another trip that ends after or when this starts, this is next trip.
            elif current_location_end and current_location_end >= dtstart:
                next_location = location
                next_location_start = dtstart
            # Otherwise, we're going home.
            else:
                next_location_start = current_location_end
            break;



# Pretty format the status info.
status = '{c.month}/{c.day}: {cloc} .. {n.month}/{n.day}: {nloc}'.format(c=current_location_start, cloc=current_location, n=next_location_start, nloc=next_location)
emoji = os.environ.get('SLACK_STATUS_EMOJI') or ''

# Setup the Slack API info.
slack_url = 'https://slack.com/api/users.profile.set'
slack_profile = '{"status_text":"' + status + '", "status_emoji": "' + emoji + '"}'
slack_token = os.environ.get('SLACK_API_TOKEN')

# Post the status to Slack.
post_data = {'token': slack_token, 'profile': slack_profile}
req = Request(slack_url, urlencode(post_data).encode())
resp = urlopen(req)
if resp.status == 200:
    print('Status updated: ' + status)
else:
    print(resp.read())
