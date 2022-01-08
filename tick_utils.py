import pandas as pd
from bs4 import BeautifulSoup
from flask import session
import time
from threading import Thread, Lock
from urllib.request import urlopen
import logging
user_ids = ['112446503', '107923457', '200256288']

mp_user_data = {}
per_user_locks = {}

class MpUser():
    def __init__(self, user_id, user_name, ticks):
        self.user_id = user_id
        self.user_name = user_name
        self.ticks = ticks

def fetch_user(user_id, force_fetch=False):
    if user_id in mp_user_data and not force_fetch:
        print(f'already fetched {user_id}')
        return
    if user_id not in per_user_locks:
        per_user_locks[user_id] = Lock()
    lock = per_user_locks[user_id]
    if lock.locked():
        # If the lock is not available, there's already a fetch in progress and
        # we shouldn't duplicate work. However, we don't want to return until
        # the job is done so we'll spin here.
        while lock.locked():
            time.sleep(0.5)
        return
    # Otherwise, acquire the lock and #dowork.
    lock.acquire()
    user_ticks = user_ticks_to_array(user_id)[:5] #only show 5 most recent ticks per user for development ease
    user_name = user_id_to_user_name(user_id)
    mp_user_data[user_id] = MpUser(user_id, user_name, user_ticks)
    lock.release()

def fetch_user_async(user_id):
    thread = Thread(target=fetch_user, args=(user_id,))
    thread.daemon = True
    thread.start()

def get_user_name(user_id):
    if user_id not in mp_user_data:
        fetch_user(user_id)
    return mp_user_data[user_id].user_name

def parse_ticks(ticks_url):
    user_ticks = []
    html = urlopen(ticks_url).read()
    soup = BeautifulSoup(html) 
    routes = soup.body.find_all('tr', attrs={'class':'route-row'})
    
    route_ticks = [route  for route in routes if  route.find('strong')]
    for route in route_ticks[:-36]: #terrifying magic number - 36 is the number of ticks displayed on a page
        route_name = route.find('strong').text   
        link = (route.find_all('a', href=True,attrs={'class':'text-black route-row'})[0]['href'])
        grade = route.find(attrs={'class':'rateYDS'}).text
        style = route.find('i').text
        summary = {'name': route_name,
                    'grade': grade,
                    'link': link,
                    'style': style}
        user_ticks.append(summary)
    return user_ticks 

def get_user_url(user_id):
    u = urlopen(f'https://www.mountainproject.com/user/{user_id}')
    u.geturl()
    url = u.url
    return url

def user_ticks_to_array(user_id):
    user_url = get_user_url(user_id)
    user_ticks_url = f'{user_url}/ticks'   
    ticks = parse_ticks(user_ticks_url)
    return ticks

def user_id_to_user_name(user_id):
    user_url = get_user_url(user_id)
    user_name = user_url.split('/')[5] #It's halloween, i'm letting myself get away with spooky magic numbers. This element of the split array is the user ID.
    return user_name


def get_date_from_style(tick_style):
    split_tick = tick_style.split(' ') #There is one space after the month, date, and year. format is "Oct 30, 2021 · Lead / Fell/Hung. Back to back to back knees! Cool!"
    date_string = f'{split_tick[0]} {split_tick[1]} {split_tick[2]}'
    date = pd.to_datetime(date_string)
    return date 


def knit_ticks_by_date(users):
    #this operation can probs be vectorized
    ticks_df = None
    for user_id in users:
        user_data = mp_user_data[user_id]
        user = user_data.user_name
        ticks = user_data.ticks
        for tick in ticks:
            tick_date = get_date_from_style(tick['style'])
            tick['date'] = tick_date
            tick['user'] = user
            user_ticks_df = pd.DataFrame.from_records(ticks)

        if  ticks_df is  None:
            ticks_df = user_ticks_df
        else:
            ticks_df = ticks_df.append(user_ticks_df)
    ticks_df = ticks_df.sort_values(by=['date', 'user'], ascending=False)
    return ticks_df.to_dict(orient="records")


if __name__ == '__main__':
    user_ticks = {}
    for user_id in user_ids:
        ticks = user_ticks_to_array(user_id)
        user_name = user_id_to_user_name(user_id)
        user_ticks[user_name] = ticks

    knit_ticks = knit_ticks_by_date(user_ticks)
    for tick in knit_ticks:
        print(tick)
