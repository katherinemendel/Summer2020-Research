import json
import pandas as pd
import numpy as np
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
import re

# Define credentials
consumer_key = ""
consumer_secret = ""

access_token = ""
access_token_secret = ""

# Create the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Set access token and secret
auth.set_access_token(access_token, access_token_secret)

# Create the API object while passing in auth information
api = tweepy.API(auth, wait_on_rate_limit=True) 

# Initialize VADER sentiment analysis
analyser = SentimentIntensityAnalyzer()

# Create list of mask-related keywords
mask_words = ["n95", "n-95", "n 95", "mask", "facepiece", "face piece", "wear", "facemask", "respirator ", \
    "face mask", "nonrebreathing", "ffr", "filtering", "filter", "face covering", "respirators"]

# Define function to determine where geographic information is stored
def get_best_loc(d):
    if(text["geo_source"] != "tweet_text" and text["geo_source"] != "none"):
        if(text["geo_source"] == "coordinates"):
            loc = "geo"
        else:
            loc = text[text["geo_source"]]
        if(("country_code") in loc and ("state") in loc):
            return text["geo_source"]
    return "none"

print("\nStarting collection\n")
print("-------------------------------------------------------------------------------------------------------------------------------------------------------------------")

# Loop through all tweets for the specified days [range(start_day, end_day+1), change month in file_name variable]
for num in range(3, 7):
    file_name = 'en_geo_2020-03-'+ str(num).zfill(2)
    print('\nBeginning collection for:\t'+file_name+'\n')

    # Declare empty list to store tweet information
    tweets = []
    count = 0
    mn_total_count = 0

    # Open json file

    #'/Users/katiemendel1/Desktop/collected-twitter-data/GeoCoV19/Mar/json/'+file_name+'.json'
    for line in open('/Users/katiemendel1/Desktop/collected-twitter-data/GeoCoV19/Mar/json/'+file_name+'.json', 'r'):
        # Load next line into dictionary
        text = json.loads(line)

        """
        Geo_source: this field shows one of the four values: (i) coordinates, (ii) place, (iii) user_location, or (iv) tweet_text.
        The value depends on the availability of these fields. However, priority is given to the most accurate fields if available. 
        The priority order is coordinates, places, user_location, and tweet_text. For instance, when a tweet has GPS coordinates, the 
        value will be "coordinates" even though all other location fields are present. If a tweet does not have GPS, place, and user_location
        information, then the value of this field will be "tweet_text" if there is any location mention in the tweet text.
        """
        # Check for location data
        best_loc = get_best_loc(text)
        if(best_loc != "none"):
            # Limit tweets to those in the US
            if(text[best_loc]["country_code"] == "us"):
                # Limit tweets to those in a specific state
                if(text[best_loc]["state"] == "Minnesota"):
                    # Increment total state count
                    mn_total_count += 1
                    # Check if county location available
                    if(("county") in text[best_loc]):
                        # Redefine text and hashtags
                        ftext=""
                        # Fetch full text tweet
                        try:
                            tweet = api.get_status(text["tweet_id"], tweet_mode='extended')
                            # Make sure to get full text of tweet no matter the type
                            if (tweet.full_text.startswith("RT @")):
                                ftext = tweet.retweeted_status.full_text
                            else:
                                ftext = tweet.full_text
                        # Put in placeholder if tweet is deleted
                        except:
                            ftext = 'deleted'
                        
                        # Mark tweets mentioning mask keywords
                        mask = False
                        for word in mask_words:
                            if ftext.find(word) >= 0:
                                mask = True


                        # Calculate sentiment score
                        ptext = re.sub(r"http\S+", "", ftext)
                        ptext = re.sub(r"@\w+", "", ptext)
                        
                        # Remove stopwords:
                        ptext = ' '.join([w for w in ptext.split() if w not in stopwords.words("english")])
                        
                        #hashtags = ' '.join(re.findall(r"#(\w+)", ptext))

                        # Calculate sentiment score of preprocessed text using VADER
                        score = analyser.polarity_scores(ptext)["compound"]

                        # Add all information about relevant tweets to list
                        tweets.append([text["tweet_id"], text["created_at"], text["user_id"], text["geo_source"], text[best_loc]["county"], ftext.replace('\n',' '), mask, score])
                        
                        # Print progress
                        #print(json.dumps(json.loads(line), indent=2))
                        count +=1
                        if(count % 500 == 0):
                            print("\t Collecting...")

    # Put tweets into pandas dataframe
    df = pd.DataFrame(tweets, columns=["tweet_id", "created_at", "user_id",  "geo_source", "county", "full_text", "mask", "sentiment_score"])

    # Remove rows for deleted tweets
    df = df[df.full_text != 'deleted']

    # Write all information to csv file
    #'/Users/katiemendel1/Desktop/collected-twitter-data/GeoCoV19/Mar/csv/'+file_name+'.csv'
    df.to_csv('/Users/katiemendel1/Desktop/collected-twitter-data/GeoCoV19/Mar/csv/'+file_name+'.csv')
    print('\n', df.head())
    print('\nCollection of '+ str(mn_total_count) +' tweets from MN complete for:\t'+file_name)
    print("\n-------------------------------------------------------------------------------------------------------------------------------------------------------------------")

print("\nCollection complete\n")