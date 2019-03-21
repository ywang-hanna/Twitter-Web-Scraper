import sys
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def loadkeys(filename):
    """"
    load twitter api keys/tokens from CSV file with form
    consumer_key, consumer_secret, access_token, access_token_secret
    """
    with open(filename) as f:
        items = f.readline().strip().split(', ')
        return items


def authenticate(twitter_auth_filename):
    """
    Given a file name containing the Twitter keys and tokens,
    create and return a tweepy API object.
    """
    consumer_key, consumer_secret, access_token, access_token_secret = loadkeys(twitter_auth_filename)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    return api


def fetch_tweets(api, name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    create a list of tweets where each tweet is a dictionary with the
    following keys:

       id: tweet ID
       created: tweet creation date
       retweeted: number of retweets
       text: text of the tweet
       hashtags: list of hashtags mentioned in the tweet
       urls: list of URLs mentioned in the tweet
       mentions: list of screen names mentioned in the tweet
       score: the "compound" polarity score from vader's polarity_scores()

    Return a dictionary containing keys-value pairs:

       user: user's screen name
       count: number of tweets
       tweets: list of tweets, each tweet is a dictionary

    For efficiency, create a single Vader SentimentIntensityAnalyzer()
    per call to this function, not per tweet.
    """
    user = api.get_user(name)
    output = dict()
    output['user'] = name
    output['count'] = user.statuses_count
    tweets = list()
    sid = SentimentIntensityAnalyzer()
    for status in tweepy.Cursor(api.user_timeline, id = name).items(100):
        tweet = dict()
        tweet['id'] = status.id
        tweet['created'] = status.created_at.date()
        tweet['retweeted'] = status.retweet_count
        tweet['text'] = status.text
        tweet['hashtags'] = status.entities['hashtags']
        tweet['urls'] = [url['url'] for url in status.entities['urls']]
        tweet['mentions'] = [name['screen_name'] for name in status.entities['user_mentions']]
        tweet['score'] = sid.polarity_scores(status.text)['compound']
        tweets.append(tweet)
    output['tweets'] = tweets
    return output


def fetch_following(api,name):
    """
    Given a tweepy API object and the screen name of the Twitter user,
    return a list of dictionaries containing the followed user info
    with keys-value pairs:

       name: real name
       screen_name: Twitter screen name
       followers: number of followers
       created: created date (no time info)
       image: the URL of the profile's image

    To collect data: get a list of "friends IDs" then get
    the list of users for each of those.
    """
    ids = api.friends_ids(name)
    output = list()
    for id in ids:
        info = dict()
        friend = api.get_user(id)
        info['name'] = friend.name
        info['screen_name'] = friend.screen_name
        info['followers'] = friend.followers_count
        info['created'] = friend.created_at.date()
        info['image'] = friend.profile_image_url
        output.append(info)
    return output
