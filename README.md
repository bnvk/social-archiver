Social Archiver
===============

A simple Python tool that downloads your pictures and private messages from Facebook and creates Mbox formatted email of your private conversations that can be imported into any standards compliant email client that can read Mbox files.

### Warning - this tool is not quite ready for use yet

Unless you already have a Facebook App auth token, this tool will not function correctly and do what it is supposed to. I'm working on this as much as possible, but development takes time. If you are handy with Python, feel free to get in touch and help ~ [Brennan Novak](https://brennannovak.com ) or [@brennannovak](https://github.com/brennannovak )
 

### Setup

Copy `config.yaml.template` and change the name to `config.yaml`

Go "Create a New App" on Facebook's [developer platform](https://developers.facebook.com)

Edit the Facebook config values in config.yaml with the values Facebook gives you

Install python dependencies `$ pip install -r requirements.txt`


### Use

From the command line run `$ python grab.py`
