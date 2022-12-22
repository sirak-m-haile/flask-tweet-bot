import base64
import hashlib
import os
import re
import json
import requests
from requests.auth import AuthBase, HTTPBasicAuth
from requests_oauthlib import OAuth2Session, TokenUpdated
from flask import Flask, request, redirect, session, url_for, render_template
import db_ops as dbOps

TOKEN_KEY = 'session_token'
SCOPES = ["tweet.read", "tweet.write", "users.read", "offline.access"]
RESULT_SIZE = 100

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
redirect_uri = os.environ.get("REDIRECT_URI")

auth_url = "https://twitter.com/i/oauth2/authorize"
token_url = "https://api.twitter.com/2/oauth2/token"
code_verifier = base64.urlsafe_b64encode(os.urandom(30)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")

COUNT_400s = 0
tweet_texts = set()

app = Flask(__name__)
app.secret_key = os.urandom(50)

def create_tweet(payload, token):
    global COUNT_400s

    response = post_tweet(payload, token).json()
    print(response)
    status_code = response.get('status')
    text = response.get('detail')
    if status_code is not None:
        if status_code == 400 or status_code == 503:
            if COUNT_400s < 3:
                COUNT_400s = COUNT_400s+1
            else:
                raise Exception(
                    "Too many 400s: {} {}".format(status_code, text)
                )
        elif status_code != 201 and status_code != 403:
            raise Exception(
                "Request returned an error: {} {}".format(status_code, text)
            )
        else:
            COUNT_400s = 0
    
        print("Response code: {}, Response message: {}".format(status_code, text))


def replace_mentions(tweet_text):
    tokens = tweet_text.split()
    updated_tokens = []
    index = 0
    for token in tokens:
        if token[0] != '@':
            updated_tokens.append(token)

    return " ".join(updated_tokens).strip()

def post_tweet(payload, token):
    return requests.request(
        "POST",
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers={
            "Authorization": "Bearer {}".format(token["access_token"]),
            "Content-Type": "application/json",
        }
    )

def search_tweets(query, user_handle, hashtags, start_time, end_time):
    headers = {"Authorization": "Bearer {}".format(BEARER_TOKEN)}

    url = "https://api.twitter.com/2/tweets/search/recent"
    search_string = query.format(user_handle, hashtags)
    query_params = {
        'query': search_string, 
        'tweet.fields': 'text,created_at', 
        'start_time': start_time, 
        'end_time': end_time,
        'max_results': RESULT_SIZE
    }
    response = requests.request("GET", url, headers=headers, params=query_params)

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def create_session():
    twitter = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=SCOPES)
    authorization_url, state = twitter.authorization_url(
        auth_url, code_challenge=code_challenge, code_challenge_method="S256"
    )
    return {twitter: twitter, authorization_url: authorization_url, state: state }

def make_token(twitter, code):
    return twitter.fetch_token(
        token_url=token_url,
        client_secret=client_secret,
        code_verifier=code_verifier,
        code=code
    )

def refresh_token(twitter, token):
    print(token.get("refresh_token"))
    refreshed_token = twitter.refresh_token(
        token_url=token_url+'/',
        refresh_token=token.get("refresh_token"),
        client_id=client_id.encode('utf8'),
        client_secret=client_secret.encode('utf8'),
        header = {
            'User-Agent': 'main/0.0.1',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + token.get("access_token"),
            'include_client_id': True,
            'grant_type': 'refresh_token'
        }
    )
    print(refreshed_token)
    save_token(refreshed_token)
    return refreshed_token

def save_token(token):
    st_token = '"{}"'.format(token)
    j_token = json.loads(st_token)
    dbOps.update('INSERT OR REPLACE INTO key_value_store(key, value) VALUES (?,?)', (TOKEN_KEY, j_token))

def get_token():
    row = dbOps.query('SELECT value FROM key_value_store WHERE key = ?', (TOKEN_KEY,))
    saved_token = row["value"]
    bb_t = saved_token.replace("'", '"')
    return json.loads(bb_t)

def save_search_query_spec(input):
    id = input.get('id')
    hashtags = input.get('hashtags')
    start_date_time = input.get('start_date_time')
    end_date_time = input.get('end_date_time')

    validate_search_query_input(hashtags, start_date_time, end_date_time)

    if id is None:
        id = dbOps.update('INSERT INTO search_queries(hashtags, start_date_time, end_date_time) VALUES(?,?,?)', 
            (hashtags, start_date_time, end_date_time))
    else:
        dbOps.update('UPDATE search_queries SET hashtags = ?, start_date_time = ?, end_date_time = ? WHERE id = ?', 
            (hashtags, start_date_time, end_date_time, id))

    return id

def get_search_query_spec(id):
    validate_id(id)
    return dbOps.query('SELECT id, hashtags, start_date_time, end_date_time FROM search_queries WHERE id = ?', (id,))

def validate_search_query_input(hashtags, start_date_time, end_date_time):
    return True

def validate_id(id):
    return True
