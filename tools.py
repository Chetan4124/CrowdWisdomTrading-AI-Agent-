import snscrape.modules.twitter as sntwitter
import pandas as pd
from crewai import Agent, Task, Crew, Process, Tool
import os
import tweepy
from dotenv import load_dotenv

load_dotenv()

class TwitterTools:

    @Tool("Search Tweets")
    def search_tweets(query: str, limit: int = 100) -> str:
        """Searches for tweets based on a query and returns a list of dictionaries containing tweet information.
        Each dictionary includes 'username', 'displayname', 'url', and 'content'.
        This tool is for general tweet content search, not for detailed user profiles.
        """
        tweets_list = []
        try:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                if i > limit:
                    break
                tweets_list.append({
                    "username": tweet.user.username,
                    "displayname": tweet.user.displayname,
                    "url": tweet.url,
                    "content": tweet.content,
                })
            return str(tweets_list)
        except Exception as e:
            return f"Error searching tweets: {e}"

    @Tool("Search X Users")
    def search_x_users(usernames: list[str]) -> str:
        """Searches for X (Twitter) user profiles based on a list of usernames and returns detailed information.
        This includes 'username', 'displayname', 'followersCount', 'url', and 'avg_posts_per_week' (approximated).
        Requires Twitter API v2 Bearer Token set in .env as TWITTER_BEARER_TOKEN.
        """
        bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
        if not bearer_token:
            return "Error: TWITTER_BEARER_TOKEN not found in .env. Please set it up for detailed user search."

        client = tweepy.Client(bearer_token)
        user_data = []

        for username in usernames:
            try:
                # Get user by username
                response = client.get_user(username=username, user_fields=["public_metrics", "created_at", "profile_image_url"])
                user = response.data

                if user:
                    # Get recent tweets to calculate avg_posts_per_week
                    # This is an approximation and might not be perfectly accurate due to API limits and data availability
                    tweets_response = client.get_users_tweets(id=user.id, tweet_fields=["created_at"], max_results=100)
                    tweets = tweets_response.data
                    
                    avg_posts_per_week = "N/A"
                    if tweets and user.created_at:
                        # Calculate the time difference in weeks
                        from datetime import datetime, timedelta
                        time_diff = datetime.now(user.created_at.tzinfo) - user.created_at
                        weeks_since_creation = time_diff.days / 7

                        if weeks_since_creation > 0:
                            # Count tweets in the last 2 weeks for 'avg_posts_per_week' if possible or use total for approximation
                            recent_tweets_count = 0
                            for tweet in tweets:
                                if datetime.now(tweet.created_at.tzinfo) - tweet.created_at < timedelta(weeks=2):
                                    recent_tweets_count += 1
                            avg_posts_per_week = round(recent_tweets_count / 2, 2) # Average over last 2 weeks
                        else:
                            avg_posts_per_week = len(tweets) # If user is very new, use total tweets

                    user_data.append({
                        "username": user.username,
                        "displayname": user.name,
                        "followersCount": user.public_metrics["followers_count"],
                        "url": f"https://twitter.com/{user.username}",
                        "avg_posts_per_week": avg_posts_per_week
                    })
                else:
                    user_data.append({
                        "username": username,
                        "displayname": "N/A",
                        "followersCount": "N/A",
                        "url": f"https://twitter.com/{username}",
                        "avg_posts_per_week": "N/A",
                        "error": "User not found or inaccessible"
                    })
            except tweepy.errors.TweepyException as e:
                user_data.append({
                    "username": username,
                    "displayname": "N/A",
                    "followersCount": "N/A",
                    "url": f"https://twitter.com/{username}",
                    "avg_posts_per_week": "N/A",
                    "error": f"Tweepy error for {username}: {e}"
                })
            except Exception as e:
                user_data.append({
                    "username": username,
                    "displayname": "N/A",
                    "followersCount": "N/A",
                    "url": f"https://twitter.com/{username}",
                    "avg_posts_per_week": "N/A",
                    "error": f"General error for {username}: {e}"
                })
        return str(user_data)
