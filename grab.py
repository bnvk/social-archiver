import sys
import MimeWriter
import base64
import StringIO
import facebook
import os
import json
import time
import operator
from operator import itemgetter
from urlparse import urlparse
from urlparse import parse_qs
from datetime import datetime

# Facebook User Authenticated Token
user_token = ""

# Creae Graph Object
graph = facebook.GraphAPI(user_token)

# Saves Profiles To Disk in json & jpg
def get_profile(pid):

    if not os.path.exists("profiles/" + pid + ".json"):

        if pid == '/me':
            photo_path = "you/"
            profile_path = "you/"
        else:
            photo_path = "friends_photos/"
            profile_path = "friends/"

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
        with open(profile_path + profile['id'] + ".json", "w") as outfile:
            json.dump(profile, outfile, indent=4)



# Saves list of friends profiles & pictures
def get_friends():

    friends = graph.get_connections("me", "friends")
    output = []

    # Save Friends list
    with open("friends.json", "w") as outfile:
        json.dump(friends, outfile, indent=4)

    # Proce Each Friend
    for friend in friends['data']:
        print "fetching " + friend['id'] + "..."
        get_profile(friend['id'])


# Process Message
def process_message_plain(message):    
    out = ''
    if message['message']:
        out += message['created_time'] + ", " + message['from']['name'] + " wrote:\n"
        out += message['message'] + '\n'
        out += "\n"
    return out

def process_message_html(message):

    # To (Cc: recipients)
    to_addr = []
    for to in message['to']['data']:
        if to['id'] != message['from']['id']:
          to_addr.append(to['name'] + "<" + to['email'] + ">")

    # Build text/html
    out = '      <div class="h-entry">\n'
    out += '        <time class="dt-published" datetime="' + message['created_time'] + '">' + message['created_time'] + '</time>\n'
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
            if 'image_data' in attachment and 'url' in attachment['image_data']:
                out += '        <span class="p-photo">' + attachment['id'] + '</span>\n'
            else:
                out += '        <span class="p-media">' + attachment['id'] + '</span>\n'
    out += '      </div>\n'

    return out


def process_message_attachments(message):
    attachments = []
    if 'attachments' in message:
        for attachment in message['attachments']['data']:
        
            if 'image_data' in attachment:
                url = attachment['image_data']['url']
                media = 'photos'
            else:
                url = ''
                media = 'files'

            # Save Attachment
            fh2 = open('messages_attachments/' + media + '/' + attachment['name'], "wb")
            fh2.write(url)
            fh2.close()

            attachments.append(dict({ 'name': attachment['name'], 'mime': attachment['mime_type'] }))

    return attachments


# Get Conversations
def get_conversations(until): #self, paging):

    if (until == 'start'):
        #print 'Now running first'
        #result = graph.get_object('/me', limit='1000000', fields='id,name,conversations')
        conversations = json.loads(open('messages.json').read())
        # Save Profile Data
        with open("messages.json", "w") as outfile:
            json.dump(result['conversations'], outfile, indent=4)
    else:
        print 'Now running ' + until
        conversations = graph.get_object('/me/inbox', limit="1000000", until=until)

    # Profile 
    profile = dict({ 'name': result['name'], 'email': result['id'] + '@facebook.com' })

    # Parse QS for paging
    parse_result = urlparse(result['conversations']['paging']['next'])
    query_string = parse_qs(parse_result[4])

    # Save Messages Data
    for conversation in result['conversations']['data']:

        print "Processing " + conversation['id']

        # Create Directory
        if not os.path.exists("messages/"):
            os.makedirs("messages/")

        # Container Message
        headers     = 'From social-archiver'
        header_user = profile['name'] + ' <' + profile['email'] + '>'
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
                email = (to['name'] + ' <' + to['email'] + '>').encode('utf-8')
                if email not in header_cc and to['email'] != profile['email']:
                    header_cc.append(email)
                    names.append(to['name'])

            # Process Parts
            plain += process_message_plain(message)
            html += process_message_html(message)
            attachments.append(process_message_attachments(message))

        # Headers
        message = StringIO.StringIO()
        writer = MimeWriter.MimeWriter(message)
        writer.addheader('From', header_user)
        writer.addheader('Cc', ', '.join(header_cc))
        writer.addheader('Subject', 'Conversation with ' + str(len(header_cc)) + ' people')
        writer.startmultipartbody('mixed')
        
        # Text part
        part = writer.nextpart()
        part.addheader('Content-Disposition', 'inline')
        part.addheader('Content-Transfer-Encoding', 'base64')
        body = part.startbody('text/plain; charset=utf-8')
        body.write(plain.encode('base64'))

        # HTML part
        part = writer.nextpart()
        part.addheader('Content-Disposition', 'inline')
        part.addheader('Content-Transfer-Encoding', 'base64')
        body = part.startbody('text/html; charset=utf-8')
        body.write((html + '  </body>\n</html>\n').encode('base64'))

        # Attachments
        #part = writer.nextpart()
        #part.addheader('Content-Transfer-Encoding', 'base64')
        #body = part.startbody('image/jpeg')
        #base64.encode(open('messages_attachments/kitten.jpg', 'rb'), body)
        #print attachments

        # Finish off
        writer.lastpart()

        # Output
        output = message.getvalue()

        # Save TXT
        f = open("messages/" + conversation['id'], "w")
        f.write(output.encode('utf-8'))
        f.close()

    # print "next: " + query_string['until'][0]
    #self.until = until
    #if query_string['until'][0] is not None:
    #    self.set_until(query_string['until'][0])

#get_profile('/me')
#get_friends()

get_conversations('start')



# Geneate a page with this to make manually deleting friends easier
# <a href="http://m.facebook.com/3621161" onClick="window.open(this.href, this.target, 'width=500,height=600'); return false;"> Unfriend Name</a>
