import praw
import os
import configparser

if not os.path.exists("config.ini"):
    print("Please run the setup_reddit.py script before running this script.")
    exit(1)
else:
    config = configparser.ConfigParser()
    config.read('config.ini')
    if config.has_section('REDDIT_AUTH'):
        if not config.has_option('REDDIT_AUTH', 'client_id'):
            print("Malformed config. Please run setup_reddit.py script.")
            exit(1)
        if not config.has_option('REDDIT_AUTH', 'client_secret'):
            print("Malformed config. Please run setup_reddit.py script.")
            exit(1)
    else:
        print("Malformed config. Please run setup_reddit.py script.")
        exit(1)

print("Gathering subreddits from 1st account")

reddit_first_user = praw.Reddit(client_id=config['REDDIT_AUTH']['client_id'],
    client_secret=config['REDDIT_AUTH']['client_secret'],
    refresh_token=config['REDDIT_AUTH']['refreshtoken_one'],
    user_agent="testscript by u/fakebot3")

first_user_subs= list(reddit_first_user.user.subreddits(limit=None))

reddit_second_user = praw.Reddit(client_id=config['REDDIT_AUTH']['client_id'],
    client_secret=config['REDDIT_AUTH']['client_secret'],
    refresh_token=config['REDDIT_AUTH']['refreshtoken_two'],
    user_agent="testscript by u/fakebot3")


print("Subscribing subbreddits from first account to second.")

for sub in first_user_subs:
    reddit_second_user.subreddit(sub.display_name).subscribe()
    print("Subscribed to ", sub.display_name)