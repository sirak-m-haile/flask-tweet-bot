import db_ops
import json
import os
import main
import requests
import time

BEARER_TOKEN = os.environ.get("BEARER_TOKEN")
TWEET_SEARCH_SPEC_ID = os.environ.get("TWEET_SEARCH_SPEC_ID")
USER_HANDLE = os.environ.get('HANDLE')
TWEET_SEARCH_QUERY = 'from:{} -is:quote -is:retweet {}'
RESULT_SIZE = 100

twitter, authorization_url, state = main.create_session()
token = main.get_token()

def tweet_from_history():
    search_tweet_spec = main.get_search_query_spec(TWEET_SEARCH_SPEC_ID)
    hashtags = search_tweet_spec["hashtags"]
    start_time = search_tweet_spec["start_date_time"]
    end_time = search_tweet_spec["end_date_time"]

    json_response = main.search_tweets(query=TWEET_SEARCH_QUERY, user_handle=USER_HANDLE, hashtags=hashtags, start_time=start_time, end_time=end_time)
    data = json_response.get('data')

    if data is None:
        return

    count = 0
    for t in json_response["data"]:
        print("{} https://api.twitter.com/2/tweets/{}".format(t["text"],t["id"]))
        if count < RESULT_SIZE:
            main.create_tweet({"text": t["text"] }, token)
            count = count + 1
            time.sleep(15)

if __name__ == "__main__":
    tweet_from_history()
