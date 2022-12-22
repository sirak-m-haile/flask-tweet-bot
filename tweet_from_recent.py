import db_ops
import json
import os
import main
import requests
import time

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
TWEET_SEARCH_SPEC_ID = os.environ.get("TWEET_SEARCH_SPEC_ID")
USER_HANDLE = os.environ.get('HANDLE')
TWEET_SEARCH_QUERY = '-from:{} -is:quote -is:retweet {}'
RESULT_SIZE = 100

twitter, authorization_url, state = main.create_session()
token = main.get_token()

tweet_texts = set()

def tweet_from_recent():
    global token
    search_tweet_spec = main.get_search_query_spec(TWEET_SEARCH_SPEC_ID)
    hashtags = search_tweet_spec["hashtags"]
    start_time = search_tweet_spec["start_date_time"]
    end_time = search_tweet_spec["end_date_time"]

    json_response = main.search_tweets(query=TWEET_SEARCH_QUERY, user_handle=USER_HANDLE, hashtags=hashtags, start_time=start_time, end_time=end_time)

    count = 0
    for t in json_response["data"]:
        print("{}: {}".format(t["created_at"],t["text"]))
        if count < RESULT_SIZE:
            no_mention_tweet = main.replace_mentions(t["text"])

            if len(tweet_texts.intersection(no_mention_tweet)) == 0:
                tweet_texts.add(no_mention_tweet)
                print(no_mention_tweet)
                # Enable refresh of the token when making a request
                # token = main.refresh_token(twitter, token)
                main.create_tweet({"text": no_mention_tweet }, token)

                count = count + 1
                time.sleep(20)

if __name__ == "__main__":
    tweet_from_recent()

