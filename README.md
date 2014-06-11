Social Archiver
===============

A simple Python tool that downloads your pictures and private messages from Facebook and creates Mbox formatted email of your private conversations that can be imported into any standards compliant email client that can read Mbox files.

### Warning - this tool is not quite ready for use yet

Unless you already have a Facebook App auth token, this tool will not function correctly and do what it is supposed to. I'm working on this as much as possible, but development takes time. If you are handy with Python, feel free to get in touch and help ~ [Brennan Novak](https://brennannovak.com ) or [@brennannovak](https://github.com/brennannovak )
 

### Initial Setup

Copy `config.yaml.template` and change the name to `config.yaml`

Install python dependencies `$ pip install -r requirements.txt`

Now you have two options with how to proceed. One is using Facebooks Graph Explorer to generate your auth token. The other is to create your own Facebook "App" and generate your auth tokens that way. The first option is fine if you're doing a one time export and deleting your account. The later is better if you want to keep using Facebook and periodically re-download updates.


### Setup Using Graph Explorer

* Go to Facebook's [Developer Platform](https://developers.facebook.com) page. 

* Edit the Facebook config values in config.yaml with the values Facebook gives you


### Setup Using App

* Go to Facebook's [Developer Platform](https://developers.facebook.com)

* Click on top menu "Apps" and then "Create a New App" 

* Open the `config.yaml` file you created in step 1

* Copy the "App ID" on Facebook into the field `facebook_app_id` in config.yaml

* Copy the "App Secret" on Facebook into the field `facebook_secret` in config.yaml


### Use The Tool

From the command line run `$ python grab.py`


