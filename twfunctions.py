
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
from logging.handlers import TimedRotatingFileHandler
 
import logging

from dateutil import parser
import codecs


from flatten_dict import flatten

#flatdict.FlatDict(
import ast



class Work():

    def __init__(self,jsonp):

        self.logger = self.create_rotating_log(jsonp)
        
    #----------------------------------------------------------------------
    def create_rotating_log(self,path):
        """
        Creates a rotating log
        """
        logger = logging.getLogger("Rotating Log")
        logger.setLevel(logging.INFO)
     

        handler = TimedRotatingFileHandler(path, when='M')
        
        logger.addHandler(handler)

        return logger

def flatten_dict(d):
    def expand(key, value):
        if isinstance(value, dict):
            return [ (key + '.' + k, v) for k, v in flatten_dict(value).items() ]
        else:
            return [ (key, value) ]

    items = [ item for k, v in d.items() for item in expand(k, v) ]

    return dict(items)

def saver(result,wk,jsonout,emitkeys = False):

    rf = flatten_dict(result)
    rfd = {}


    if(emitkeys):
        for e in emitkeys:
            v = rf[e]
            rfd[e] = v
            
        jd = json.dumps(rfd)
    else:
        jd = json.dumps(rf)
    wk.logger.info(jd)
    

def saverMany(collResults,wk,jsonout,emitkeys = False):

    for result in collResults:
        rf = flatten_dict(result)
        rfd = {}
        
        if(emitkeys):
            for e in emitkeys:
                v = rf[e]
                rfd[e] = v
                
            jd = json.dumps(rfd)
        else:
            jd = json.dumps(rf)

        wk.logger.info(jd)
    
def saverMany_GetUser(collResults,wk,jsonout,emitkeys = False):

    for result in collResults:
        rf = flatten_dict(result)
        rfd = {}
        
        #if 'energia' in rf['description'].lower():  
            # print("############################################")
            # print(rf)
            # print("############################################")
        if(emitkeys):
            for e in emitkeys:
                try:
                    v = rf[e]
                    rfd[e] = v
                except Exception as exc:
                    if str(exc)=="'status.text'":
                        print("WARNING: no key status.text for user",rf['screen_name'])
                        v = ''
                        rfd[e] = v
                    else:
                        raise Exception(e)

                    
                # print("############################################")
                # print(rfd)
                # print("############################################")
                jd = json.dumps(rfd)
        else:
            jd = json.dumps(rf)

        wk.logger.info(jd)


def getSearch(tw,words,jsonout,emitkeys,sleep_time = 5.1):
    results = tw.cursor(tw.search, q=words, count = 100,return_pages = True)
    idx = 0

    wk = Work(jsonout)
    
    for result in results:

        coll = []
        for res in result:
            res['search_words'] = words
            coll.append(res)

        #saver(res,wk,jsonout,emitkeys)
        saverMany(coll,wk,jsonout,emitkeys)

        idx += 1
        time.sleep(sleep_time)
        print(idx)

def getSearchUser(screen_names, tw,words,jsonout,emitkeys,sleep_time = 5.1):

    print(words)

    results = tw.search_users(q=words, page=50, count = 20, return_pages = True)
    #results = tw.search(q=words, count = 100, return_pages = True)
    idx = 0

    # target = ["energia", "energy", "gas"]

    wk = Work(jsonout)
    
    coll = []
    print(results)
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    for res in results:
        # print(res)
        # print("screen_names:",screen_names)
        print(res['screen_name'])
        print(res['description'])
        print("************************************")
        if res['screen_name'] not in screen_names:
            # for t in target:
            #if t in res['description'].lower():
            screen_names.add(res['screen_name'])
            res['search_words'] = words
            coll.append(res)
                # break



    print("COLL:")
    print(coll)
    print("$$$$$$$$$$$$$$")


    #saver(res,wk,jsonout,emitkeys)
    #saverMany(coll,wk,jsonout,emitkeys)
    saverMany_GetUser(coll,wk,jsonout,emitkeys)

    idx += 1
    time.sleep(sleep_time)
    print(idx)

    return screen_names

def getTimeline(tw,user,jsonout,emitkeys,sleep_time = 1.1):
    results = tw.cursor(tw.get_user_timeline, screen_name=user, count = 200,return_pages = True)
        
    idx = 0

    wk = Work(jsonout)

    counterT = 0
    for result in results:

        coll = []
        for res in result:
            res['user_screen_name'] = user
            coll.append(res)
            counterT+= 1
        if(counterT > 200):
            return

        #saver(res,wk,jsonout,emitkeys)
        saverMany(coll,wk,jsonout,emitkeys)


        idx += 1
        time.sleep(sleep_time)
        print(idx)



def getFriends(tw,user,jsonout,emitkeys,sleep_time = 61.0):
    results = tw.cursor(tw.get_friends_list, screen_name=user, count = 200,return_pages = True)
    idx = 0

    wk = Work(jsonout)

    counterT = 0
    for result in results:

        coll = []
        for res in result:
            #for r in res.keys():
                #print(r)
            #sys.exit()
            res['user_screen_name'] = user # SERVE AD ASSOCIARE IL FRIEND ALL'UTENTE IN FASE DI ANALISI SUCCESSIVA!
            coll.append(res)
            counterT+= 1
        if(counterT > 100):
            return

        #saver(res,wk,jsonout,emitkeys)
        saverMany(coll,wk,jsonout,emitkeys)


        idx += 1
        time.sleep(sleep_time)
        print(idx)


def getFollowers(tw,user,jsonout,emitkeys):
    #followers = tw.get_followers_list(screen_name=user)
    #print(len(followers))

    wk = Work(jsonout)
    
    followers = []
    
    # This is to go through paginated results
    next_cursor = -1

    cnt = 1
    
    while(next_cursor):
        # Getting the user's followers (should all be 1 line)
        get_followers = tw.get_followers_list(screen_name=user,count=200,cursor=next_cursor)

        # For each user returned from our get_followers

        for follower in get_followers["users"]:

            follower['user_screen_name'] = user # SERVE AD ASSOCIARE IL FRIEND ALL'UTENTE IN FASE DI ANALISI SUCCESSIVA!
            
            # Add their screen name to our followers list
            followers.append(follower)#["screen_name"].encode("utf-8"))
            
            next_cursor = get_followers["next_cursor"]   

            time.sleep(2)

            print(follower)
            cnt+=1

        saverMany(followers,wk,jsonout,emitkeys)
  
            
    print(len(followers))

def getFriends_new(tw,user,jsonout,emitkeys):
    #followers = tw.get_followers_list(screen_name=user)
    #print(len(followers))

    wk = Work(jsonout)
    
    followers = []
    
    # This is to go through paginated results
    next_cursor = -1

    cnt = 1
    
    while(next_cursor):
        # Getting the user's followers (should all be 1 line)
        get_followers = tw.get_friends_list(screen_name=user,count=200,cursor=next_cursor)

        # For each user returned from our get_followers

        print(len(get_followers))
        
        for follower in get_followers["users"]:

            follower['user_screen_name'] = user # SERVE AD ASSOCIARE IL FRIEND ALL'UTENTE IN FASE DI ANALISI SUCCESSIVA!
            
            # Add their screen name to our followers list
            followers.append(follower)#["screen_name"].encode("utf-8"))
            
            next_cursor = get_followers["next_cursor"]   

            #time.sleep(2)

            #print(follower)
            cnt+=1

        saverMany(followers,wk,jsonout,emitkeys)
        time.sleep(61)
            
    print(len(followers))
