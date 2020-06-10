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
popularUsers = ["BarackObama", "justinbieber", "katyperry", "taylorswift13", "POTUS", "ladygaga", "TheEllenShow", "ArianaGrande", "KimKardashian", "jtimberlake"]

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
    worksheet.write(row, 7, "class")

    row += 1

    for tweet in tweets:
        worksheet.write_string(row, 0, str(tweet.id))
        worksheet.write_string(row, 1, str(tweet.created_at))
        # Write full text of tweet
        if (tweet.full_text.startswith("RT @")):
            text = tweet.retweeted_status.full_text
            worksheet.write(row, 3, "True")
            favorites = tweet.retweeted_status.favorite_count
        else:
            text = tweet.full_text
            worksheet.write(row, 3, "None")
            favorites = tweet.favorite_count
        
        # Replace special characters
        text = emoji.demojize(text)
        text = re.sub("\n", " ", text)
        text = re.sub("'", "\\\'", text)
        text = re.sub("’", "\\\'", text)
        text = re.sub("\"", "", text)
        text = re.sub(":", " ", text)

        worksheet.write(row, 2, "'" + text + "'")
        worksheet.write_string(row, 4, str(tweet.in_reply_to_status_id))
        worksheet.write_string(row, 5, str(tweet.retweet_count))
        worksheet.write_string(row, 6, str(favorites))
        worksheet.write(row, 7, "?")
        row += 1

    workbook.close()

    # Prepare for file format conversions
    csvFileName = "/Users/katiemendel 1/Desktop/collected-twitter-data/csv/" + username + ".csv"
    arffFileName = "/Users/katiemendel 1/Desktop/collected-twitter-data/arff/" + username + ".arff"

    # Convert from XLSX to CSV format
    read_file = pd.read_excel("/Users/katiemendel 1/Desktop/collected-twitter-data/excel/" + username + ".xlsx")
    read_file.to_csv(csvFileName, index=None, header=True)

    print("\nFiles ready for user:\t\t", username)

print("\n---------------------------------------------------------------------\n")

print("Tweet collection and processing complete\n\n")