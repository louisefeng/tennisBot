import praw
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# appearance indicates page has changed to h2h2 page of selected players
page_ind1 = 'Post your comment or tip'
page_ind2 = 'No previous matches'


def search():
    driver = webdriver.Chrome()
    driver.get('https://matchstat.com/tennis/head-to-head')
    modal_open = driver.find_elements_by_class_name('modal-header')
    if len(modal_open) > 0:
        modal_open[0].find_element_by_class_name('close').click()

    try:
        # search for the h2h2 results of p1, p2
        field1 = driver.find_element_by_id('h2h-search-player1')
        field1.send_keys(in1)
        field2 = driver.find_element_by_id('h2h-search-player2')
        field2.send_keys(in2)
        field2.send_keys(Keys.ENTER)

        source = driver.page_source
        timeout = 5
        # wait for page to change
        while source.find(page_ind1) == -1:
            if timeout == 0:
                #invalid input
                return no_matchups_response(in1, in2)
            if source.find(page_ind2) > 0:
                return no_matchups_response(in1, in2)
            time.sleep(3)
            source = driver.page_source
            timeout -= 1

        driver.quit()
        return source
    except:
        return None


def parse():
    p1_stats = soup.find_all('tbody')[0]
    p2_stats = soup.find_all('tbody')[1]

    p1 = find_relevant_stats(p1_stats)
    p2 = find_relevant_stats(p2_stats)

    return (p1, p2)


def find_relevant_stats(stats_tbl):
    player = {}
    for row in stats_tbl.find_all('tr'):
        stat = row.find_all('td')
        if stat[0].get_text() == 'Wins:':
            player['Wins'] = stat[1].get_text()
        elif stat[0].get_text() == 'Ranking:':
            player['Ranking'] = stat[1].get_text()
    return player


def construct_h2h_response():
    player_names = [p.get_text() for p in soup.find_all('h2')]

    p1['Name'] = player_names[0]
    p2['Name'] = player_names[1]

    p1_wins = float(p1['Wins'])
    p2_wins = float(p2['Wins'])
    total = p1_wins + p2_wins

    if p1_wins > p2_wins:
        more_wins, ratio = (p1['Name'].split(' ')[1], p1_wins / total)
    else:
        more_wins, ratio = (p2['Name'].split(' ')[1], p2_wins / total)

    ratio = str(round(ratio * 100, 2)) + '%'
    msg = 'Head to head matchup for {0}({1}) vs. {3}({4}):  \n{0}: {2}  \n{3}: {5}  \n{6} leads, winning {7} of the matches'.format(
    p1['Name'], p1['Ranking'], p1['Wins'], p2['Name'], p2['Ranking'], p2['Wins'], more_wins, ratio)
    comment.reply(msg)


def no_matchups_response(p1, p2):
    comment.reply('1 No matchups recorded for ' + p1 + ' and ' + p2)


bot = praw.Reddit(user_agent='tennisBot v0.1',
                  client_id='KCeWX6_08vz_Dg',
                  client_secret='-gVfboq7GhvaWahjY6z4_SOIf68',
                  username='littlepanda888',
                  password='pikaprincess8')


# set up PRAW
subreddit = bot.subreddit('testingground4bots')
comments = subreddit.stream.comments()
for comment in comments:
    text = comment.body.lower()
    if text.startswith('!tennisbot'):
        stripped = text.replace('!tennisbot','').split('vs. ')
        in1 = stripped[0][1:] if len(stripped) > 0 and re.match(r'^[a-zA-Z ]+$', stripped[0]) else '\'no result\' '
        in2 = stripped[1] if len(stripped) > 1 and re.match(r'^[a-zA-Z ]+$', stripped[0]) else '\'no result\''
        if in1 == '\'no result\'' or in2 == '\'no result\'':
            no_matchups_response(in1, in2)
            continue
        res_page = search()
        if res_page:
            soup = BeautifulSoup(res_page, "html.parser")
            p1, p2 = parse()
            construct_h2h_response()
        else:
            comment.reply('Error fetching data. Cross your fingers and try again maybe?')
