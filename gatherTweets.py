# Extracts tweets based off of list of usernames provided
# Cleans data and exports in XLSX, CSV and ARFF formats
#
# @Author Katie Mendel - github.com/katmendy
# @Date June, 2020
#

# Import required packages
import tweepy
import datetime
import xlsxwriter
import sys
import pandas as pd
import emoji
import re
import nltk
#import TextBlob
import textblob
from textblob import TextBlob


# Define credentials
consumer_key = "X"
consumer_secret = "X"

access_token = "X"
access_token_secret = "X"

# Create the authentication object
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
# Set access token and secret
auth.set_access_token(access_token, access_token_secret)

# Create the API object while passing in auth information
api = tweepy.API(auth) 

# Set list of handles for extraction
#popularUsers = ["BarackObama", "POTUS"]
popularUsers = ["justinbieber", "katyperry", "taylorswift13", "ladygaga", "TheEllenShow", "ArianaGrande", "KimKardashian", "jtimberlake", "rihanna", "RealChalamet"]

# Set user from command line
#username = sys.argv[1]
#popularUsers = [username]

# Set time period (March 20, 2020 - Present)
startDate = datetime.datetime(2020, 3, 20, 0, 0, 0, 0)
endDate = datetime.datetime.now().replace(microsecond=0)

# Print list of users
print("\nBeginning tweet collection for users:\n")
for user in popularUsers:
    print("\t",user, " ")

# Extract tweets from timeline for each user
for username in popularUsers:

    # Print user information
    print("\n---------------------------------------------------------------------\n")
    print("Fetching tweets for user:\t", username)
    print("\n\tStart date:\t", startDate)
    print("\tEnd date:\t", endDate)
    print("\n")

    # NOT IMPLEMENTED YET
    # Define search words
    #searchWords = ["corona", "coronavirus", "covid", "sarscov2", "nCov", "covid-19", "ncov2019", "covid19", "pandemic", "quarantine", "social distancing"]

    # Check for tweets within desired date range
    tweets = []
    tmpTweets = api.user_timeline(username, tweet_mode='extended')
    for tweet in tmpTweets:
        if tweet.created_at < endDate and tweet.created_at > startDate:
            tweets.append(tweet)

    # Fetch info about desired tweets
    while (tmpTweets[-1].created_at > startDate):
        print("\tLast Tweet @", tmpTweets[-1].created_at, " - fetching some more")
        tmpTweets = api.user_timeline(username, max_id = tmpTweets[-1].id, tweet_mode='extended')
        for tweet in tmpTweets:
            if tweet.created_at < endDate and tweet.created_at > startDate and (tweet not in tweets): 
                # NOT YET IMPLEMENTED
                # Filtering out off-topic tweets
                #if any(s in tweet.text.lower() for s in searchWords):
                    tweets.append(tweet)


    # NOT YET IMPLEMENTED
    # Prepare NRC files for use
    #filepath = "NRC-Emotion-Lexicon-v0.92/NRC-emotion-lexicon-wordlevel-alphabetized-v0.92.txt"
    #emolex_df = pd.read_csv(filepath,  names=["word", "emotion", "association"], skiprows=45, sep='\t')


    # Write to excel file
    workbook = xlsxwriter.Workbook("/Users/katiemendel 1/Desktop/collected-twitter-data/excel/" + username + ".xlsx")
    worksheet = workbook.add_worksheet()
    row = 0

    # Add descriptive header
    worksheet.write_string(row, 0, "id")
    worksheet.write_string(row, 1, "created_at")
    worksheet.write(row, 2, "full_text")
    worksheet.write(row, 3, "retweeted_status")
    worksheet.write_string(row, 4, "in_reply_to_status_id")
    worksheet.write_string(row, 5, "retweet_count")
    worksheet.write_string(row, 6, "favorite_count")
    worksheet.write(row, 7, "interaction")
    worksheet.write(row, 8, "sentiment")
    worksheet.write(row, 9, "polarity")
    worksheet.write(row, 10, "subjectivity")
    worksheet.write(row, 11, "class")

    row += 1

    for tweet in tweets:

        # Check if tweet is a retweet and fetch full text
        if (tweet.full_text.startswith("RT @")):
            text = tweet.retweeted_status.full_text
            retweet = True
            favorites = tweet.retweeted_status.favorite_count
            mention = True
        else:
            text = tweet.full_text
            retweet = False
            favorites = tweet.favorite_count
            if('@' in text):
                mention = True
            else:
                mention = False


        # Replace special characters
        text = emoji.demojize(text)
        text = re.sub("tears_of_joy", "laughing", text)
        text = re.sub("sign_of_the_horns", "rock_on", text)
        text = re.sub(r"http\S+", "", text)
        text = re.sub("\n", " ", text)
        text = re.sub("'", "\\\'", text)
        text = re.sub("’", "\\\'", text)
        text = re.sub("\"", "", text)
        text = re.sub(":", " ", text)
        text = re.sub("_", " ", text)
        
        if(text != ""):
            worksheet.write_string(row, 0, str(tweet.id))
            worksheet.write_string(row, 1, str(tweet.created_at))
            worksheet.write(row, 2, "'" + text.lower() + "'")
            worksheet.write(row, 3, str(retweet))
            worksheet.write_string(row, 4, str(tweet.in_reply_to_status_id))
            worksheet.write_string(row, 5, str(tweet.retweet_count))
            worksheet.write_string(row, 6, str(favorites))
            worksheet.write(row, 7, str(mention))
            if(TextBlob(text).sentiment.polarity > 0):
                worksheet.write(row, 8, "pos")
            else:
                worksheet.write(row, 8, "neg")
            worksheet.write(row, 9, str(TextBlob(text).sentiment.polarity))
            worksheet.write(row, 10, str(TextBlob(text).sentiment.subjectivity))
            worksheet.write(row, 11, "?")
            row += 1

    workbook.close()

    # Prepare for file format conversions
    csvFileName = "/Users/katiemendel 1/Desktop/collected-twitter-data/csv/" + username + ".csv"

    # Convert from XLSX to CSV format
    read_file = pd.read_excel("/Users/katiemendel 1/Desktop/collected-twitter-data/excel/" + username + ".xlsx")
    read_file.to_csv(csvFileName, index=None, header=True)

    print("\nFiles ready for user:\t\t", username)

print("\n---------------------------------------------------------------------\n")

print("Tweet collection and processing complete\n\n")
