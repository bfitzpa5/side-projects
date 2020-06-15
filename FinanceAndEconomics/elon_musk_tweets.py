# -*- coding: utf-8 -*-
"""
Created on Thu Jun 11 17:03:16 2020

@author: Brendan Non-Admin
"""

import os
import pandas as pd
import requests
import base64
import json
from twitter_config import tc
import datetime as dt

_base_url = r'https://api.twitter.com/'

def authenticate():
    key_secret = '{}:{}'.format(tc['api_key'], tc['api_secret_key']).encode('ascii')
    b64_encoded_key = base64.b64encode(key_secret)
    b64_encoded_key = b64_encoded_key.decode('ascii')
    auth_url = '{}oauth2/token'.format(_base_url)
    auth_headers = {
        'Authorization': 'Basic {}'.format(b64_encoded_key),
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
    }
    auth_data = {
        'grant_type': 'client_credentials'
    }
    auth_resp = requests.post(auth_url, headers=auth_headers, data=auth_data)
    access_token = auth_resp.json()['access_token']
    return access_token


def scrape_elon_musk_tweets_premium_api(access_token, next_id):
    request_headers = {
        'Authorization': 'Bearer {}'.format(access_token),
        #"Content-Type": "application/json",
    }
    request_params = {
        'query': 'from:elonmusk lang:en',
        #'query': 'snow OR cold OR blizzard',
        #'count': 200,
    }
    if next_id:
        request_params['next'] = next_id
    
    url = 'https://api.twitter.com/1.1/tweets/search/fullarchive/nlpanalysis.json'
    response = requests.get(url, headers=request_headers, params=request_params)

    json_data = response.json()
    df = pd.DataFrame(json_data['results'])
    
    return df

def scrape_elon_musk_tweets(access_token, max_id=None, tesla_tweets_only=False):
    request_headers = {
        'Authorization': 'Bearer {}'.format(access_token)    
    }
    request_params = {
        'screen_name': 'elonmusk',
        'count': 200,
    }
    if max_id:
        request_params['max_id'] = max_id
    
    url = '{}1.1/statuses/user_timeline.json'.format(_base_url)
    response = requests.get(url, headers=request_headers, params=request_params)
    
    json_data = response.json()
    df = pd.DataFrame(json_data)
    
    
    try:
        next_max_id = df.id.min() - 1
    except Exception as e:
        print(request_params)
        if 'errors' in df.columns.tolist():
            print(df.errors)
        raise e
        
    
    if tesla_tweets_only:
        mask = df.text.str.contains('Tesla')
        df = df.loc[mask, :]
    
    return df, next_max_id

frames = list()
next_max_id = None
access_token = authenticate()
while True:
    df, next_max_id = scrape_elon_musk_tweets(access_token, max_id=next_max_id)
    frames.append(df)
    if next_max_id is None:
        break
    
df = pd.concat(frames)