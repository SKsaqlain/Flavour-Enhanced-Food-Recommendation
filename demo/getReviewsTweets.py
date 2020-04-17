
import tweepy
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
import json
import pandas as pd
import csv
import re #regular expressionfrom textblob import TextBlob
import json
import time
#from textblob import TextBlob
import string

#import preprocessor as p ->>>this package is not getting installed on windows

consumer_key = 'consumer_key'
consumer_secret = 'consumer_secret'
access_key= 'access_key'
access_secret = 'access_secret'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)



def getTweets(foodName="",cnt=100,pg=100,startDate='2018-01-01',endDate='2020-01-02'):
    if(len(foodName)>0):
        #tweetEntry=[]
        for page in tweepy.Cursor(api.search,q=foodName,count=cnt,include_rts=False,since=startDate,tweet_mode='extended',lang='en').pages(pg):
            with open(foodName+".json","w") as fr:
                for status in page:        
                    status=status._json
                    tweet=status
                    #tweetEntry.append([foodName,tweet["user"]["id"],tweet["full_text"]])
                    json.dump([foodName,tweet["user"]["id"],tweet["full_text"]],fr,indent=2)
        
    else:
        print("invalid food name")


dishFile=open("dishName.txt","r")
dishRaw=dishFile.readlines()

print(len(dishRaw))
for i,ele in enumerate(dishRaw):
    
    if(i>0):
        try:
            print(i)
            getTweets(foodName=ele.strip("\n"),cnt=100,pg=100)
        except:
            time.sleep(15*60)
            print(i)
            getTweets(foodName=ele.strip("\n"),cnt=100,pg=100)
            

