Documentation
=============

This is a work in progress. Would love help refining

### Facebook Messages API

Using the Facebook Graph API you a blobs of JSON. While the Social Archiver tool downloads from many different endpoints, the main endpoint relevant to this documentation is the [Conversations Resource](https://developers.facebook.com/docs/graph-api/reference/v2.0/conversation)


### Directory & File Name

How to store personal messages downloaded to a local disk. There are a few goals this should achieve

* Gracefully scale to 10 / 100s of thousands of messages
* Segment messages intelligently so that it informs of the conversations contained therein
* Be easy to index by other software applications and services
* Be easy for a person to browse via their operating system's GUI file manager & the command line

Organization by date is the first most obvious idea

/2014/05/conversation-id.file
/2014/05/25/conversation-id.file

This would scale nicely for importing data from multiple different services

/2014/05/facebook-conversation-id.file
/2014/05/twitter-conversation-id.file

Another direction may be to organize based on conversation or contact id at the highest level, then cascade into more granular date directories.

/contact-id/2014/05/
/facebook-contact-id/2014/05/

One downside is, this is less intuitive to normal people browsing their filesystem and seeing long strings of numbers compared to the date hierarchy. However, many of these social sites have usernames of the person(s) in a thread, which are more human

/rickjames/2014/05/conversation-id.file
/rickjames/2014/05/facebook-conversation-id.file
/rickjames-salliejoe-1202033566/facebook-conversation-id.file (third segment is a user with no username)


### The "From" Value

How to express the "from" aspect of this message to have the most amount of data integrity and flexibility in respect to parsing it. this SHOULD offer a graceful way to accept data from multiple siloed social media sources (Facebook, Twitter, etc...). The first example works nicely in YML style markup.

name: Brennan Novak
source: facebook.com
id: 653983917

name: Brennan Novak
source: twitter.com
id: 17958179

Here is a version that resembles email addresses, this would lend itself more to UNIX Mbox style formats

653983917@facebook.com
Brennan Novak <653983917@facebook.com>
17958179@twitter.com
Brennan Novak <17958179@twitter.com>

Facebook's platform currently seems to sometimes support receiving email sent to a UI style @address. Twitter absolutely does not support it.


### UNIX Mbox or Maildir Representation

Here are some notes about how the email file is currently being written and why.

* Each email message is a file that contains a segmented Facebook conversation thread
* Media are embedded as base64 encoded email attachments, they are also saved to disk as normal files 
* The Plain text part of the email has a simple chat style conversation that should degrade nicely to older clients
* The HTML part of the email contains Microformat data that can be extracted with a Microformats parser to
    * This will allow random clients that don't follow mime standards perfectly to still display all the data perfectly
    * This keeps scale & load of single sentence messages in high volumes in a meaningful way


```
From social-archiver
To: Brennan Novak <id@facebook.com>
From: Person Who Started The Chat <id@facebook.com>
Cc: Other PEople <id@facebook.com>, In the chat <id@facebook.com>
MIME-Version: 1.0
Content-Type: multipart/mixed; boundary=RANDOMCRAPSTRING

--RANDOMCRAPSTRING
Content-Type: multipart/alternative; boundary=OTHERBOUNDARYSTRING
Content-Transfer-Encoding: 8bit

--OTHERBOUNDARYSTRING
Content-Type: text/plain; charset=utf-8
Content-Disposition: inline

25 May 2014 3:01, Mr. Mork: 
Nano, nano! Some message text here!

25 May 2014 03:01, Ms. Mindy:
Moar message text will go here


--OTHERBOUNDARYSTRING
Content-Type: text/html; charset=utf-8
Content-Disposition: inline
Content-Transfer-Encoding: base64

BASE 64 encoded:
    
<div class="h-entry">
  <time class="dt-published" datetime="2014-05-01T10:48:00+00:00">2014-05-01 10:48:00</time>
  <a href="mailto:123456789@facebook.com" class="p-author h-card">
    <span class="p-name">Mr. Mork</span>
    <span class="u-uid" hidden="true">123456789</span>
    <span class="u-url" hidden="true">https://facebook.com/123456789</span>
  </a>
  <span class="e-content p-name">Nano, nano! Some message text here!</span>
  <span class="u-uid" hidden="true">m_mid.6d2c628</span>
  <span class="p-category" hidden="true">inbox</span>
  <span class="p-category" hidden="true">read</span>
  <span class="p-category" hidden="true">source:web</span>
</div>
<div class="h-entry">
  <time class="dt-published" datetime="2014-05-01T10:49:00+00:00">2014-05-01 10:49:00</time>
  <a href="mailto:987654321@facebook.com" class="p-author h-card">
    <span class="p-name">Ms. Mindy</span>
    <span class="u-uid" hidden="true">987654321</span>
    <span class="u-url" hidden="true">https://facebook.com/987654321</span>
  </a>
  <span class="e-content p-name">Moar message text will go here</span>
  <span class="u-uid" hidden="true">m_mid.453ic628</span>
  <span class="p-category" hidden="true">inbox</span>
  <span class="p-category" hidden="true">read</span>
  <span class="p-category" hidden="true">source:web</span>  
</div> 


--OTHERBOUNDARYSTRING--

--RANDOMCRAPSTRING
Content-Type: image/jpeg
Content-Disposition: attachment
Content-Transfer-Encoding: base64

BASE64 ENCODED IMAGE DATA

--RANDOMCRAPSTRING
Content-Type: image/jpeg
Content-Disposition: attachment
Content-Transfer-Encoding: base64

BASE64 ENCODED IMAGE DATA

--RANDOMCRAPSTRING--
```
