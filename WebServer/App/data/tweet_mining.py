import tweepy
from tweepy import Cursor
import unicodecsv
from unidecode import unidecode
import sys
import os

# The following 3 functions simulate a progress bar in the terminal output
# title = string shown before progress bar
# 0 <= x <= 100 amount of progress made
def startProgress(title):
    global progress_x
    sys.stdout.write(title + ": [" + "-"*40 + "]" + chr(8)*41)
    sys.stdout.flush()
    progress_x = 0

def progress(x):
    global progress_x
    x = int(x * 40 // 100)
    sys.stdout.write("#" * (x - progress_x))
    sys.stdout.flush()
    progress_x = x

def endProgress():
    sys.stdout.write("#" * (40 - progress_x) + "]\n")
    sys.stdout.flush()

def downloadTweets(tweetData):
    # Read authentication keys from .dat file
    print("trying to find twitter authentication keys from: "+ os.getcwd() + "/keys.dat")
    keys = open("keys.dat","r")

    # Authentication and connection to Twitter API.
    consumer_key = keys.readline()[:-1]
    consumer_secret = keys.readline()[:-1]
    access_key = keys.readline()[:-1]
    access_secret = keys.readline()[:-1]

    # Close authentication file
    keys.close()

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    # Usernames whose tweets we want to gather.
    users = ["realDonaldTrump","tedcruz","LindseyGrahamSC","SpeakerRyan","BarackObama","GovGaryJohnson","BernieSanders","HillaryClinton","DrJillStein"]

    with open(tweetData, 'wb') as file:
        writer = unicodecsv.writer(file, delimiter = ',', quotechar = '"')
        # Write header row.
        writer.writerow(["politician_name",
                        "politician_username",
                        "tweet_text",
                        "tweet_retweet_count",
                        "tweet_favorite_count",
                        "tweet_hashtags",
                        "tweet_hashtags_count",
                        "tweet_urls",
                        "tweet_urls_count",
                        "tweet_user_mentions",
                        "tweet_user_mentions_count",
                        "tweet_by_trump"])
        
        # For each Twitter username in the users array
        for user in users:
            # Gather info specific to the current user.
            user_obj = api.get_user(user)
            user_info = [user_obj.name,
                         user_obj.screen_name]

            startProgress("Downloading tweets from" + user)
            # Maximum amounts of tweets to retrieve
            max_tweets = 1000;

            # Count the amount of tweets retrieved
            count = 0;

            # Get 1000 most recent tweets for the current user.
            for tweet in Cursor(api.user_timeline, screen_name = user).items(max_tweets):

                # Show progress
                progress(count/(max_tweets/100)) 

                # Increase count for tweets
                count += 1

                # Remove all retweets.
                if tweet.text[0:3] == "RT ":
                    continue

                # Get info specific to the current tweet of the current user.
                tweet_info = [unidecode(tweet.text),
                              tweet.retweet_count,
                              tweet.favorite_count]

                # Below entities are stored as variable-length dictionaries, if present.
                hashtags = []
                hashtags_data = tweet.entities.get('hashtags', None)
                if(hashtags_data != None):
                    for i in range(len(hashtags_data)):
                        hashtags.append(unidecode(hashtags_data[i]['text']))

                urls = []
                urls_data = tweet.entities.get('urls', None)
                if(urls_data != None):
                    for i in range(len(urls_data)):
                        urls.append(unidecode(urls_data[i]['url']))

                user_mentions = []
                user_mentions_data = tweet.entities.get('user_mentions', None)
                if(user_mentions_data != None):
                    for i in range(len(user_mentions_data)):
                        user_mentions.append(unidecode(user_mentions_data[i]['screen_name']))
                        
                tweet_by_trump = 0
                if(user_obj.screen_name=='realDonaldTrump'):
                    tweet_by_trump = 1

                more_tweet_info = [', '.join(hashtags),
                                   len(hashtags),
                                   ', '.join(urls),
                                   len(urls),
                                   ', '.join(user_mentions),
                                   len(user_mentions),tweet_by_trump]

                # Write data to CSV.
                writer.writerow(user_info + tweet_info + more_tweet_info)



            endProgress()

            print("Wrote tweets by %s to CSV." % user)

if __name__ == "__main__":
    downloadTweets('tweets.csv')