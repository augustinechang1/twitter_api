import pandas as pd
import json
import time

# for converting params {} into URL syntax
import urllib.parse
import urllib

import twitter
import re



ORIGINAL_USER_NAME = 'ScottsFlowerNYC'
ORIGINAL_USER_ID = '211262113'

FLORAL_REGEX = re.compile("(Flor(a|e|i)|(flower|bloom|tulip|plant|fleur|flor|enchantedflo))")

api = twitter.Api(
		consumer_key=consumer_key,
		consumer_secret=consumer_secret,
		access_token_key=access_token_key,
		access_token_secret=access_token_secret
)

tweets = []
followers = []

def query_twitter():

	user_tweets = get_search_screen_name(ORIGINAL_USER_NAME)

	# will hold actual tweets
	add_tweets(tweets, user_tweets)

	user_followers = get_followers(ORIGINAL_USER_ID)

	# will hold actual followers
	add_users(followers, user_followers)

	### CONVERT TO DATAFRAME
	df_followers = pd.DataFrame(followers)

	# top 200 followers by number of followers
	top_followers = df_followers.sort_values(by=['followers_count'], ascending=False)[:120]

	# randomly select 150 screen_names from the top 200 followers with most followers
	# random_top_followers = top_followers['screen_name'].sample(n=100, random_state=1)
	random_top_followers = top_followers['screen_name']

	# convert to list for iteration
	random_screen_names = random_top_followers.tolist()

	# query the API with list of top screen names
	get_search_list(random_screen_names)

	# convert list of tweets to dataframe
	df_tweets = pd.DataFrame(tweets)

	# covnert created_at into datetime
	df_tweets['created_at'] = pd.to_datetime(df_tweets['created_at'], infer_datetime_format=True)

	# df_followers
	# df tweets

	###################################
	###################################
	#######        TO CSV      ########
	###################################
	###################################

	df_tweets.to_csv('tweets.csv')
	df_followers.to_csv('followers.csv')

def name_matches_floral(name):
	matches = FLORAL_REGEX.search(name.lower())
	if matches == None:
		return False
	else:
		return True

def get_search_screen_name(screen_name):
	params = {'q': 'from:' + screen_name,'count': 100}
	search = get_search(params)
	return search

def get_search(params={}):
	encoded_params = urllib.parse.urlencode(params)
	results = api.GetSearch(raw_query=encoded_params)
	print("___  {} ___ RESULTS".format(len(results)))
	return results

def dict_from_tweet(tweet):
	return {
		'text': tweet.text,
		'created_at': tweet.created_at,
		'favorite_count': tweet.favorite_count,
		'retweet_count': tweet.retweet_count,
		'user': tweet.user.screen_name,
		'user_id': tweet.user.id
	}

def add_tweets(tweet_list=[], tweets=[]):
	'''
	input: list to hold tweet objs
	input: list of tweets returned by API
	output: list of parsed tweet {}
	'''
	for t in tweets:
		tweet_list.append(dict_from_tweet(t))
	return tweet_list

###################################
###################################
####### TWITTER FOLLOWERS #########
###################################
###################################

def dict_from_user(user):
	return {
	   'user_id': user.id,
	   'screen_name': user.screen_name,
		'name': user.name,
		'description': user.description,
	   'followers_count': user.followers_count,
	   'friends_count': user.friends_count,
	}

def add_users(user_list=[], users=[]):
	'''
	input: list to hold user objs
	input: list of users returned by API
	output: list of parsed user {}
	'''
	for u in users:
		if name_matches_floral(u.screen_name):
			user_list.append(dict_from_user(u))
	return user_list

def get_followers(user_id):
	return api.GetFollowers(user_id=user_id)

###################################
###################################
####### GET TWEETS BY USER ########
###################################
###################################

def get_search_list(list_of_screen_names):
	for name in list_of_screen_names:
		user_tweets = get_search_screen_name(name)
		print("{} had {} tweets".format(name, len(user_tweets)))
		add_tweets(tweets, user_tweets)

# call function
query_twitter()

