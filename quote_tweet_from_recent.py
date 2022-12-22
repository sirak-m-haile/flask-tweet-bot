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

# def search_twitter_recent(query, start_time, end_time):
#     headers = {"Authorization": "Bearer {}".format(BEARER_TOKEN)}

#     url = "https://api.twitter.com/2/tweets/search/recent"
#     search_string = '-from:{} -is:quote -is:retweet {}'.format(SEARCH_HANDLE, query)
#     query_params = {
#         'query': search_string, 
#         'tweet.fields': 'text,created_at', 
#         'start_time': start_time, 
#         'end_time': end_time,
#         'max_results': RESULT_SIZE
#     }
#     response = requests.request("GET", url, headers=headers, params=query_params)

#     print(response.status_code)

#     if response.status_code != 200:
#         raise Exception(response.status_code, response.text)
#     return response.json()

def quote_tweet_from_recent():
    quote_text = "#AmharaRevolution"
    search_tweet_spec = main.get_search_query_spec(TWEET_SEARCH_SPEC_ID)
    hashtags = search_tweet_spec["hashtags"]
    start_time = search_tweet_spec["start_date_time"]
    end_time = search_tweet_spec["end_date_time"]

    json_response = main.search_tweets(query=TWEET_SEARCH_QUERY, user_handle=USER_HANDLE, hashtags=hashtags, start_time=start_time, end_time=end_time)

    count = 0
    print("Got {} results".format(len(json_response["data"])))
    for t in json_response["data"]:
        print("{}: {}: {}".format(count, t["created_at"],t["text"]))
        if count < RESULT_SIZE:
            main.create_tweet({"text": quote_text, "quote_tweet_id": t["id"] }, token)
            count = count + 1
            time.sleep(15)

if __name__ == "__main__":
    quote_tweet_from_recent()