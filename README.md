Social Archiver
===============

A simple tool written in python 2.7 that downloads your pictures, data, and private messages from Facebook. Once downloaded the tool creates Mbox formatted emails of your private conversations that can be imported into any standards compliant email client that can read Mbox files.


### WARNING - this tool is not ready for prime time yet

Unless you already have a Facebook App auth token, this tool will not function correctly and do what it is supposed to. I'm working on this as much as possible, but development takes time. If you are handy with Python, feel free to get in touch and help ~ [Brennan Novak](https://brennannovak.com ) or [@brennannovak](https://github.com/brennannovak )
 

### Setup

Copy `config.yaml.template` and change the name to `config.yaml`

Install python dependencies `$ pip install -r requirements.txt`

Now you have two options with how to proceed. Option A) is using Facebooks Graph Explorer to generate your auth token. Option B) is to create your own Facebook "App" and generate your auth tokens that way. The first option is fine if you're doing a one time export and deleting your account. The later is better if you want to keep using Facebook and periodically re-download updates (feature not implemented yet).


### Setup A) Using Graph Explorer

* Go to Facebook's [Developer Platform](https://developers.facebook.com) page. 
* Edit the Facebook config values in config.yaml with the values Facebook gives you


### Setup B) Create New App

* Go to Facebook's [Developer Platform](https://developers.facebook.com)
* Click on top menu "Apps" and then "Create a New App" 
* Open the `config.yaml` file you created in step 1
* Copy the "App ID" on Facebook into the field `facebook_app_id` in config.yaml
* Copy the "App Secret" on Facebook into the field `facebook_secret` in config.yaml


### Using The Tool

From the command line run `$ python grab.py`

There are a few arguments you can pass to the tool:

* `friends` downloads basic data & pictures of your friends
* `photos` downloads photos you are tagged in
* `messages` downloads your private messages and formats them as Mbox style emails

By default the tool only gets your profile data & photo. To choose extra downloads pass one of the arguments `$ python grab.py messages` it's ok to all all three arguments at once :P


