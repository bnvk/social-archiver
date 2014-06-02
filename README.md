Social Archiver
===============

A simple Python tool that downloads your pictures and private messages from Facebook and creates Mbox formatted email of your private conversations that can be imported into any standards compliant email client that can read Mbox files.


### Setup

Copy `config.yaml.template` and change the name to `config.yaml`

Go "Create a New App" on Facebook's developer platform [https://developers.facebook.com]

Edit the Facebook config values in config.yaml with the values Facebook gives you

Install python dependencies `$ pip install requirements.txt`


### Use

From the command line run `$ python grab.py`