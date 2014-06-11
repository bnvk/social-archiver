import yaml
import sys
import MimeWriter
import base64
import StringIO
import facebook
import os
import json
import time
import operator
import hashlib
import requests
import shutil
from operator import itemgetter
from urlparse import urlparse
from urlparse import parse_qs
from datetime import datetime
from time import strptime

# Load App Config Values
config_yaml = open('config.yaml')
config = yaml.load(config_yaml)
config_yaml.close()

# Creae Graph Object
graph = facebook.GraphAPI(config['facebook_user_token'])


# Make Downloads Folders
def make_directories(): 
    if not os.path.exists("downloads/facebook/"):
        os.makedirs("downloads/facebook/")
    if not os.path.exists("downloads/facebook/friends/"):
        os.makedirs("downloads/facebook/friends/")
    if not os.path.exists("downloads/facebook/friends_photos/"):
        os.makedirs("downloads/facebook/friends_photos/")
    if not os.path.exists("downloads/messages/"):
        os.makedirs("downloads/messages/")   
    if not os.path.exists("downloads/messages_attachments/"):
        os.makedirs("downloads/messages_attachments/")   
    if not os.path.exists("downloads/facebook/you/"):
        os.makedirs("downloads/facebook/you/")
    if not os.path.exists("downloads/facebook/you_photos/"):
        os.makedirs("downloads/facebook/you_photos/")


# Saves Profiles To Disk in json & jpg
def get_profile(pid):

    if not os.path.exists("profiles/" + pid + ".json"):

        if pid == '/me':
            photo_path = "downloads/facebook/you/"
            profile_path = "downloads/facebook/you/"
        else:
            photo_path = "downloads/facebook/friends_photos/"
            profile_path = "downloads/facebook/friends/"

        # Get Profile & Pic
        profile = graph.get_object(pid)
        photo = graph.get_object(pid + "/picture", width="200", height="200")
        photo_large = graph.get_object(pid + "/picture", width="9999")

        if 'username' in profile:
            handle = profile['username']
        else:
            handle = profile['id']

        # Save 200px photo
        fh = open(photo_path + handle + ".jpg", "wb")
        fh.write(photo['data'])
        fh.close()

        # Save Full photo
        fh2 = open(photo_path + handle + "_full.jpg", "wb")
        fh2.write(photo_large['data'])
        fh2.close()

        # Save Profile Data
        with open(profile_path + pid + ".json", "w") as outfile:
            json.dump(profile, outfile, indent=4)


# Saves list of friends profiles & pictures
def get_friends():

    friends = graph.get_connections("me", "friends")
    output = []

    # Save Friends list
    with open("downloads/facebook/friends.json", "w") as outfile:
        json.dump(friends, outfile, indent=4)

    # Proce Each Friend
    for friend in friends['data']:
        print "fetching " + friend['id'] + "..."
        get_profile(friend['id'])


# Photos
class Photos():

    def __init__ (self):
        self.current = 0

    def test(self):

        result = graph.get_object('/me/photos', limit=100)

        # Parse QS for paging
        parse_result = urlparse(result['paging']['next'])
        query_string = parse_qs(parse_result[4])

        print parse_result
        print query_string
        print query_string['until'][0]

    def get_tagged(self, until):

        if (until == 'start'):
            print 'Now running photos start'
            result = graph.get_object('/me/photos', limit=100)
        else:
            print 'Now running photos ' + until
            result = graph.get_object('/me/photos', limit=100, until=until)
  
        # Save Photos json
        with open("downloads/facebook/you_photos.json", "w") as outfile:
            json.dump(result, outfile, indent=4)
  
        # Loop Through Pictures
        if result['data']:
            for photo in result['data']:
        
                pic_url    = photo['picture'] 
                parsed_url = urlparse(pic_url)
                split_url  = parsed_url.path.split('/')
                pic_name   = split_url[len(split_url) - 1]
        
                # Download Full Picture
                print "Downloading pic thumb_" + pic_name
                response = requests.get(url = pic_url, stream=True)
                if response.status_code == 200:
                    with open("downloads/facebook/you_photos/thumb_" + pic_name, 'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
                del response
        
                # Download Full Picture
                print "Downloading pic " + pic_name
                response = requests.get(url = photo['images'][0]['source'], stream=True)
                if response.status_code == 200:
                    with open("downloads/facebook/you_photos/" + pic_name, 'wb') as out_file:
                        shutil.copyfileobj(response.raw, out_file)
                del response
    
            # Parse QS for paging
            parse_result = urlparse(result['paging']['next'])
            query_string = parse_qs(parse_result[4])
            
            print "Restarting with until: " + query_string['until'][0]
            self.get_tagged(query_string['until'][0])

        else:
            print "Empty photos result"        


# Conversations
class Conversations():

    def __init__ (self, profile):
        self.current = 0

    def nice_datetime(self, dt):
        split = dt.split('+')[0]
        fixed = datetime(*strptime(split, "%Y-%m-%dT%H:%M:%S")[0:6])
        month = fixed.strftime('%b ')
        day_year = fixed.strftime('%d, %Y at ').lstrip('0')
        time = fixed.strftime('%H:%M').lstrip('0')
        return month + day_year + time

    # Process text/plain
    def process_plain(self, message):
        out = ''
        if message['message']:

            # Format datetime like May 25, 2014 at 3:01 PM
            out += self.nice_datetime(message['created_time']) + ", " + message['from']['name'] + ":\n"
            out += message['message'] + '\n'
            out += "\n"
        return out

    # Process text/html
    def process_html(self, message):
        out = '      <div class="h-entry">\n'
        out += '        <time class="dt-published" datetime="' + message['created_time'] + '">' + self.nice_datetime(message['created_time']) + '</time>\n'
        out += '        <a href="mailto:' + message['from']['email'] + '" class="p-author h-card">\n'
        out += '          <span class="p-name">' + message['from']['name'] + '</span>\n'
        out += '          <span class="u-uid" hidden="true">' + message['from']['id'] + '</span>\n'
        out += '          <span class="u-url" hidden="true">https://facebook.com/' + message['from']['id'] + '</span>\n'
        out += '        </a>\n'
        out += '        <span class="e-content p-name">' + message['message'] + '</span>\n'
        out += '        <span class="u-uid" hidden="true">' + message['id'] + '</span>\n'

        # Add Tags
        for tag in message['tags']['data']:
            out += '        <span class="p-category" hidden="true">' + tag['name'] + '</span>\n'

        # Check Attachments
        if 'attachments' in message:
            for attachment in message['attachments']['data']:
                if 'image_data' in attachment:
                    out += '        <span class="p-photo">' + attachment['name'] + '</span>\n'
                else:
                    out += '        <span class="p-media">' + attachment['name'] + '</span>\n'
        out += '      </div>\n'
        return out

    # Process attachments
    def process_attachments(self, message):
        output = []
        if 'attachments' in message:
            for attachment in message['attachments']['data']:
                attachment_status = 'empty'
                print "Downloading attachment " + attachment['name']
                
                # Is Image else Other
                if 'image_data' in attachment:
                    response = requests.get(url = attachment['image_data']['url'], stream=True)
                    if response.status_code == 200:
                        attachment_status = 'success'
                        with open('downloads/messages_attachments/' + attachment['name'], 'wb') as out_file:
                            shutil.copyfileobj(response.raw, out_file)
                    del response
                else:
                    # Facebook doesn't have a Graph API endpoint for attachments so use Request module
                    # http://stackoverflow.com/questions/9192430/view-attachments-in-threads
                    # https://developers.facebook.com/bugs/153137724878722?browse=external_tasks_search_results_52517d949d48d3494815922
                    response = requests.get('https://api.facebook.com/method/messaging.getattachment', params={
                            'access_token': config['facebook_user_token'], 
                            'mid': message['id'], 
                            'aid': attachment['id'],
                            'format': 'json'
                          })
                    if response.status_code == 200:
                        attachment_status = 'success'
                        json = response.json()
                        output_file = base64.b64decode(json['data'])
                        fh2 = open('downloads/messages_attachments/' + attachment['name'], 'wb')
                        fh2.write(output_file)
                        fh2.close()
                    del response

                # Add To Parent List
                output.append(dict({ 'status': attachment_status, 'name': attachment['name'], 'mime': attachment['mime_type'] }))

        return output


    def get(self, until):

        if (until == 'start'):
            print 'Now running start'
            result = graph.get_object('/me/conversations', limit=100)
        else:
            print 'Now running ' + until
            result = graph.get_object('/me/conversations', limit=100, until=until)

        # (Pass in result['conversations']['data'])
        for conversation in result['data']:

            # Create Hash cause Fbook IDs are wonky
            conversation_id = hashlib.md5(conversation['id']).hexdigest()
            print "Processing " + conversation_id + " from: " + conversation['id']

            # Container Message
            headers     = 'From social-archiver'
            header_user = profile['name'] + ' <' + profile['id'] + '@facebook.com>'
            header_cc   = []
            names       = []
            plain       = ''
            html        = '<html>\n  <body>\n' # Add CSS via http://email-standards.org
            attachments = []

            # Order by Date
            ordered_messages = sorted(conversation['messages']['data'], key=itemgetter('created_time'))

            # Loop Through Messages
            for message in ordered_messages:

                # Headers
                for to in message['to']['data']:
                    email = (to['name'] + ' <' + to['email'] + '>')
                    if email not in header_cc and to['email'] != profile['id'] + '@facebook.com':
                        header_cc.append(email)
                        names.append(to['name'])

                # Process Parts
                plain += self.process_plain(message)
                html  += self.process_html(message)
                attachments = attachments + self.process_attachments(message)

            # Headers
            header_cc_output = ', '.join(header_cc)
            header_subject_output = 'Conversation with ' + ', '.join(names)

            # Start Message
            message = StringIO.StringIO()
            writer = MimeWriter.MimeWriter(message)
            writer.addheader('From', header_user)
            writer.addheader('Cc', header_cc_output)
            writer.addheader('Subject', header_subject_output)
            writer.startmultipartbody('mixed')

            # Text part
            part = writer.nextpart()
            part.addheader('Content-Disposition', 'inline')
            body = part.startbody('text/plain; charset=utf-8')
            body.write(plain)

            # HTML part
            part = writer.nextpart()
            part.addheader('Content-Disposition', 'inline')
            body = part.startbody('text/html; charset=utf-8')
            body.write((html + '  </body>\n</html>\n'))

            # Attachments
            if attachments:
                for attach in attachments:
                    if attach['status'] == 'success':
                        print 'Adding Mime Part ' + attach['name']
                        part = writer.nextpart()
                        part.addheader('Content-Transfer-Encoding', 'base64')
                        body = part.startbody(attach['mime'])
                        base64.encode(open('downloads/messages_attachments/' + attach['name'], 'rb'), body)

            # Finish Email
            writer.lastpart()

            # Save TXT
            mbox = open("downloads/messages/" + conversation_id, "w")
            mbox.write(message.getvalue().encode('utf-8'))
            mbox.close()

        # Parse QS for paging
        parse_result = urlparse(result['paging']['next'])
        query_string = parse_qs(parse_result[4])

        print "Restarting with until: " + query_string['until'][0]
        self.get(query_string['until'][0])


# Do Defaults
print "Making directories"
make_directories()

# Get Your Profile
if os.path.isfile("downloads/facebook/you/me.json"):
    print "Getting your profile"
    #get_profile('/me')
    profile = json.loads(open('downloads/facebook/you/me.json').read())

# CL args
if 'friends' in (sys.argv):
    print "Getting friends data & pictures"
    get_friends()

if 'photos' in (sys.argv):
    print "Getting photos you are tagged in"
    myPhotos = Photos()
    myPhotos.get_tagged('start')

if 'messages' in (sys.argv):
    print "Getting your messages & attachments"
    myConversations = Conversations(profile) 
    myConversations.get('start')

print "Downloading is all done, takk :)"


# Geneate a page with this to make manually deleting friends easier
# <a href="http://m.facebook.com/3621161" onClick="window.open(this.href, this.target, 'width=500,height=600'); return false;"> Unfriend Name</a>