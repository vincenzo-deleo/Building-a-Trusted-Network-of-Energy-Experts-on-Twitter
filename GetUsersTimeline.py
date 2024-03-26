#!/usr/bin/python3
from twython import Twython

from twython import TwythonError, TwythonRateLimitError, TwythonAuthError
import twython


import time
import json
import yaml
import sys
import datetime
import re
import os
import argparse

from dateutil import parser
import codecs

from twfunctions import getSearch,getTimeline

import ast


def getCfg(yfile):
    def getEm(emitkeys):
        keys = []
        for l in emitkeys.split(","):
            keys.append(l.replace('"',"").replace("'",""))
        return keys
        
    config = open(yfile)
    yml = yaml.load(config)

    app_key = yml['APP_KEY']
    app_secret = yml['APP_SECRET']
    oauth_token = yml['OAUTH_TOKEN']
    oauth_token_secret = yml['OAUTH_TOKEN_SECRET']
    emitkeys = getEm(yml['emitkeys'])

    return app_key,app_secret,oauth_token,oauth_token_secret,emitkeys



### main



def getParse():

    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--configfile", help="Config File",default="config.yaml")
    parser.add_argument("-x", "--contentfile", help="Search Content File")
    parser.add_argument("-o", "--outfile", help="Output Json File")
    #parser.add_argument("-t", "--test", help="Dry Run of the scripts",action="store_true")

    args = parser.parse_args()


    if(args.configfile):
        configfile = args.configfile

    if(args.contentfile):
        contentfile = args.contentfile


    if(args.outfile):
        outfile = args.outfile

    return configfile,contentfile,outfile





def getWords(contentfile):
    op = open(contentfile)
    seeds = []
    m = 0
    for l in op:
        l = l.rstrip()
        sp = '"'+l+'"'
        seeds.append(sp)
        if(m > 15):
            break
        m += 1
    op.close()
    seeds = "'"+ " OR ".join(seeds) + "'"
    return seeds


def getUsers(usersfile):
    op = open(usersfile)
    users = []
    m = 0
    for l in op:
        l = l.rstrip()
        sp = l.strip()
        users.append(sp)
        m += 1
    op.close()
    return users


configfile,contentfile,outfile =  getParse()

app_key,app_secret,oauth_token,oauth_token_secret,emitkeys = getCfg(configfile)



twitter = Twython(app_key, app_secret, oauth_token, oauth_token_secret)


#words = getWords(contentfile)
users = getUsers(contentfile)

for user in users:
    try:
        getTimeline(twitter,user,outfile,emitkeys)
    except Exception as e:
        op = open("timelineErr.txt","a+")
        st = "error on %s. Exc: %s\n"%(user,str(e))
        op.write(st)
        pass
#getSearch(twitter,words,outfile,emitkeys)
