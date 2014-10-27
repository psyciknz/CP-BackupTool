#!/usr/bin/env python
import sys
import urllib
import os.path
import ConfigParser
import time
import json 
from pprint import pprint 
import argparse

def process(type, backup):
    config = ConfigParser.ConfigParser()
    if args.cfg:
        configFilename = args.cfg 
    else:
        configFilename = os.path.join(os.path.dirname(sys.argv[0]), "couch.cfg")

    print "Loading config from", configFilename
    with open(configFilename, "r") as conf:
        config.readfp(conf)

    host = config.get("CouchPotato", "host")
    port = config.get("CouchPotato", "port")
    apikey = config.get("CouchPotato", "apikey")
    if not apikey:
        raise ValueError("No apikey specified in %s" % configFilename)

    try:
        ssl = int(config.get("CouchPotato", "ssl"))
    except (ConfigParser.NoOptionError, ValueError):
        ssl = 0
   
    try:
        web_root = config.get("CouchPotato", "web_root")
    except ConfigParser.NoOptionError:
        web_root = ""


    if ssl:
        protocol = "https://"
    else:
        protocol = "http://"
    
    if type == "backup":
        url = protocol + host + ":" + port + web_root + "/api/" + apikey + "/" + "movie.list/?status=active"
        print "Opening URL:", url
        try:
            urlObj = urllib.urlopen(url)
        except IOError, e:
            print "Unable to open URL: ", str(e)
            sys.exit(1)
    
        result = json.load(urlObj)
        imdb_list = [ item["info"]["imdb"] for item in result["movies"] if 'info' in item and 'imdb' in item["info"] ]

        with open(backup, 'w') as f:
            for imdb in imdb_list:
                f.write(imdb +'\n')
        f.close()

    elif type == "restore":
        with open(backup, 'r') as f:
            imdb_list = [ line.strip() for line in f ]
        f.close()
        baseurl = protocol + host + ":" + port + web_root + "/api/" + apikey + "/" + "movie.add/?identifier="
        for imdb in imdb_list:
            url = baseurl + imdb
            print "Opening URL:", url
            try:
                urlObj = urllib.urlopen(url)
            except IOError, e:
                print "Unable to open URL: ", str(e)
                sys.exit(1)

parser = argparse.ArgumentParser(description='Backup/Restore Couchpotato wanted list',
                                formatter_class=argparse.RawTextHelpFormatter)
# Require this option
parser.add_argument('--type', metavar='backup/restore', choices=['backup', 'restore'],
                    required=True, help='')
parser.add_argument('file', help='''If backup: The file to save the wanted list to.
If restore: The file to restore from.''')
parser.add_argument('--cfg', metavar='cfg-file', help='Specify an alternative cfg file')
args = parser.parse_args()
process(args.type, args.file)
