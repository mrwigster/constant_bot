# -*- coding: utf-8 -*-
import schedule
import time
import sys
import os
import random
from tqdm import tqdm
import threading        #->added to make multithreadening possible -> see fn run_threaded

sys.path.append(os.path.join(sys.path[0],'../../'))
from instabot import Bot

bot = Bot(comments_file="comments.txt", blacklist="blacklist.txt")
bot.login()
username_logged_in = bot.username
bot.logger.info("Constant Bot-Leave running 24/7")


comments_file_name = username_logged_in+"_comments.txt"
random_user_file = bot.read_list_from_file(username_logged_in+"_username_database.txt")
random_hashtag_file = bot.read_list_from_file(username_logged_in+"_hashtag_database.txt")
friends_user_file = username_logged_in+"_friends.txt"
blacklist_file = username_logged_in+"_blacklist.txt"


#fn to return random value for separate jobs
def get_random(from_list):
    _random=random.choice(from_list)
    print("Random from ultimate.py script is chosen: \n" + _random + "\n")
    return _random

def stats(): bot.save_user_stats(bot.user_id)
def job1(): bot.like_hashtag(get_random(random_hashtag_file), amount=int(700/24))
def job2(): bot.like_timeline(amount=int(300/24))
def job3(): bot.like_followers(get_random(random_user_file), nlikes=3)
def job4(): bot.follow_followers(get_random(random_user_file))
def job5(): bot.comment_medias(bot.get_timeline_medias())
def job6(): bot.unfollow_non_followers()
def job7(): bot.follow_users(bot.get_hashtag_users(get_random(random_hashtag_file)))


def job9():  # put non followers on blacklist
    try:
        print("Creating Non Followers List")
        followings = bot.get_user_following(bot.user_id)  # getting following
        followers = bot.get_user_followers(bot.user_id)  # getting followers
        friends_file = bot.read_list_from_file(friends_user_file)  # same whitelist (just user ids)
        nonfollowerslist = list((set(followings) - set(followers)) - set(friends_file))
        with open(blacklist_file, 'a') as file:  # writing to the blacklist
            for user_id in nonfollowerslist:
                file.write(str(user_id) + "\n")
        print("removing duplicates")
        lines = open(blacklist_file, 'r').readlines()
        lines_set = set(lines)
        out = open(blacklist_file, 'w')
        for line in lines_set:
            out.write(line)
        print("Task Done")
    except Exception as e:
        print(str(e))


# function to make threads -> details here http://bit.ly/faq_schedule
def run_threaded(job_fn):
    job_thread = threading.Thread(target=job_fn)
    job_thread.start()

schedule.every(1).hour.do(run_threaded, stats)              #get stats
schedule.every(2).hours.do(run_threaded, job1)              #like hashtag
schedule.every(3).hours.do(run_threaded, job2)              #like timeline
schedule.every(1).days.at("16:00").do(run_threaded, job3)   #like followers of users from file
schedule.every(2).days.at("11:00").do(run_threaded, job4)   #follow followers
schedule.every(16).hours.do(run_threaded, job5)             #comment medias
schedule.every(1).days.at("08:00").do(run_threaded, job6)   #unfollow non-followers
schedule.every(12).hours.do(run_threaded, job7)             #follow users from hashtag from file
schedule.every(4).days.at("07:50").do(run_threaded, job9)   #non-followers blacklist

while True:
    schedule.run_pending()
    time.sleep(1)
