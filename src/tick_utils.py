import pandas as pd
from bs4 import BeautifulSoup
from urllib.request import urlopen
user_ids = ['112446503', '107923457', '200256288']

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


def knit_ticks_by_date(ticks_by_user):
    #this operation can probs be vectorized
    ticks_df = None
    for user, ticks in ticks_by_user.items():
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
