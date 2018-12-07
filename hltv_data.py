import re 
import pandas as pd
import matplotlib.pyplot as plt
import sys,time
import requests
import numpy as np
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
import os

base_url_group = [r'https://www.hltv.org/events/archive?eventType=MAJOR&eventType=INTLLAN&prizeMin=247333&prizeMax=1500000',r'https://www.hltv.org/events/archive?offset=50&eventType=MAJOR&eventType=INTLLAN&prizeMin=247333&prizeMax=1500000']
bash_link = r'https://www.hltv.org'
ranking_link = r'/ranking/teams'
ranking_index = ['position','points','player1','player2','player3','player4','player5','link']
def get_ranking_soup(year,month,day):
    link = r'https://www.hltv.org/ranking/teams/'+year+'/'+month+'/'+day
    print('get ranking from ',link)
    html = requests.get(link).text
    soup = BeautifulSoup(html,'lxml')
    return soup

def get_ranking_day(year,month):
    link = r'https://www.hltv.org/ranking/teams/2018/may/21'
    html = requests.get(link).text
    soup = BeautifulSoup(html,'lxml')
    day_url = soup.find_all("a",{"href":re.compile(r'/ranking/teams/'+year+r'/'+month+r'/(\d+)'),"class":re.compile(r'sidebar-single-line-item\s?(selected)?')})
    _day = []
    day_index = day_url[0]
    day_link = bash_link + day_index['href']
    day_html = requests.get(day_link).text
    day_soup = BeautifulSoup(day_html,'lxml')
    all_day_url = day_soup.find_all("a",{"href":re.compile(r'/ranking/teams/'+year+r'/'+month+r'/(\d+)'),"class":re.compile(r'sidebar-single-line-item\s?(selected)?')})
    for all_day_msg in all_day_url:
        all_day_num = all_day_msg['href'].split('/')[-1]
        _day.append(int(all_day_num))
    _day = list(set(_day))
    day = sorted(_day)
    return day
    
def get_team_position(header):
    m = re.compile(r'#([0-9]{1,2})')
    position = m.search(str(header))
    return position.group(1)

def get_team_link(header):
    m = re.compile(r'class="name\sjs-link"\sdata-url="(/team/[0-9]{1,6}/.{2,15})">.{2,15}</span>')
    link = m.search(str(header))
    if link:
        return bash_link + link.group(1)
    else:
        return None

def get_team_num(header):
    m = re.compile(r'class="name\sjs-link"\sdata-url="/team/([0-9]{1,6})/.{2,15}">.{2,15}</span>')
    num = m.search(str(header))
    if num:
        return num.group(1)
    else:
        return None

def get_team_name(header):
    m = re.compile(r'class="name\sjs-link"\sdata-url="/team/[0-9]{1,6}/.{2,15}">(.{2,15})</span>')
    name = m.search(str(header))
    if name:
        return name.group(1)
    else:
        return None

def get_team_points(header):
    m = re.compile(r'\(([0-9]{1,4})\spoints\)')
    points = m.search(str(header))
    if points:
        return points.group(1)
    else:
        return None

def get_team_players(con):
    m = re.compile(r'data-url="/player/[0-9]{1,6}/.{1,20}">([^<>/]{1,20})<')
    players = m.findall(str(con))
    if len(players) < 5:
        while 5-len(players):
            players.append('none') 
    return players

def get_team_data(soup):
    parents = soup.find_all("div",{"class":"bg-holder"})
    flag = 0
    for parent in parents:
        header = parent.find_all("div",{"class":"header"})[0]
        con = parent.find_all("div",{"class":"lineup-con"})[0]
        team_name = get_team_name(header)
        team_position = get_team_position(header)
        team_points = get_team_points(header)
        team_players = get_team_players(con)
        team_num = get_team_num(header)
        team_link = get_team_link(header)
        if flag == 0:
            data = pd.DataFrame([team_name,team_position,team_points,team_num,team_players[0],team_players[1],team_players[2],team_players[3],team_players[4],team_link],index=['name','position','points','num','player1','player2','player3','player4','player5','link'],columns=[team_name])
            flag = 1
        else:
            data[team_name] = pd.Series([team_name,team_position,team_points,team_num,team_players[0],team_players[1],team_players[2],team_players[3],team_players[4],team_link],index=['name','position','points','num','player1','player2','player3','player4','player5','link'])
    return data



def RateOfWinning(_map,data):
    return data.get(_map+'_win')/(data.get(_map+'_win')-data.get(_map+'_lost'))

def AllOfRate(data):
    datas = pd.Series([RateOfWinning('Cache',data),RateOfWinning('Train',data),RateOfWinning('Mirage',data),RateOfWinning('Inferno',data),RateOfWinning('Dust2',data),RateOfWinning('Overpass',data),RateOfWinning('Cobblestone',data),RateOfWinning('Nuke',data),],index=['Cache','Train','Mirage','Inferno','Dust2','Overpass','Cobblestone','Nuke'])
    return datas

def get_team_result(link):
    #link = team_match_link
    html = requests.get(link).text
    soup = BeautifulSoup(html,'lxml')
    parents = soup.find_all("tr",{"class":re.compile("group-\d (first)?")})
    _map = 'Cache|Train|Mirage|Inferno|Dust2|Overpass|Cobblestone|Nuke|Season'
    _lost = 'L|W|T'
    data = {'Cache_win':0,'Train_win':0,'Mirage_win':0,'Inferno_win':0,'Dust2_win':0,'Overpass_win':0,'Cobblestone_win':0,'Nuke_win':0,'Cache_lost':0,'Train_lost':0,'Mirage_lost':0,'Inferno_lost':0,'Dust2_lost':0,'Overpass_lost':0,'Cobblestone_lost':0,'Nuke_lost':0}
    for parent in parents:
        map_html = parent.find_all("td",{"class":"statsMapPlayed"})[0]
        time_html = parent.find_all("td",{"class":"time"})[0]
        lost_html = parent.find_all("td",{"class":re.compile("text-center match-(lost)?(won)?(tied)?\s?(lost)?(won)?")})[0]
        team_map =  re.findall(_map,str(map_html))[0]
        if team_map  == 'Season':
            continue
        team_lost = re.findall(_lost,str(lost_html))[0]
        team_time = re.findall(re.compile(r'\d{2}/\d{2}/\d{2}'),str(time_html))
        print(team_map,' ',team_lost,' ' ,team_time)
        if team_lost == 'L':
            data.update({team_map+'_lost':data.get(team_map+'_lost')-1})
        elif team_lost == 'W':
            data.update({team_map+'_win':data.get(team_map+'_win')+1})
    return data

def get_team_match_link(data,Team):
    if Team == 'Natus Vincere':
        return bash_link+"/stats/teams/matches/"+data.ix['num',Team]+'/'+'Natus%20Vincere'
    elif Team == 'Space Soldiers':
        return bash_link+"/stats/teams/matches/"+data.ix['num',Team]+'/'+'Space%20Soldiers' 
    elif Team == 'ALTERNATE aTTaX':
        return bash_link+"/stats/teams/matches/"+data.ix['num',Team]+'/'+'ALTERNATE%20aTTaX' 
    else:
        return bash_link+"/stats/teams/matches/"+data.ix['num',Team]+'/'+Team

def get_stats_team():
    url = r'https://www.hltv.org/stats/teams'
    html = requests.get(url).text
    soup = BeautifulSoup(html,'lxml')
    team_url = soup.find_all("a",{"href":re.compile(r'/stats/teams/[0-9]{1,6}/(.+)'),"data-tooltip-id":re.compile(r'.+')})
    team_name = []
    for team_link in team_url:
        team_link = team_link['href'].split('/')[-1]
        team_name.append(team_link)
    return team_name

def get_team_plot(Team,data):
    link = get_team_match_link(data,Team)
    print('Connect From',link)
    datas = get_team_result(link)
    DATA = AllOfRate(datas)
    DATA.plot(kind = 'bar')
    plt.ylim((0,1))
    plt.ylabel('Rate Of Win')
    plt.xlabel('Map')
    plt.xticks([0,1,2,3,4,5,6,7],[r'$Cache$',r'$Train$',r'$Mirage$',r'$Inferno$',r'$Dust2$',r'$Overpass$',r'$Cobblestone$',r'$Nuke$'])
    plt.show()

def get_team_base(Team,data):
    print(data.ix[:,Team])

def get_match_data(base_url_group):
    flag = 1
    for base_url in base_url_group:
        html = requests.get(base_url).text
        soup = BeautifulSoup(html,'lxml')
        img_url = soup.find_all("a",{"href":re.compile(r'/events/\d+/[\w\-]*'),"class":re.compile(r'[\s\-\w]*')})
        for url in img_url:
            url = url['href']
            match_url = url.split('/')[-1]
            match_name_group = match_url.split('-')
            match_num = url.split('/')[-2] 
            match_name = ''
            for name in match_name_group:
                name = str.title(name) 
                match_name = match_name + name + ' '
            if flag == 1:
                match_data = pd.DataFrame([match_num,match_name,match_url],index=['num','match_name','match_url'],columns=[str(flag)])
            else:
                match_data[str(flag)] = pd.Series([match_num,match_name,match_url],index=['num','match_name','match_url'])
            flag = flag + 1
    return match_data.T

def get_match_img_url(match_data,flag):
    return r'https://www.hltv.org/galleries?event=' + match_data.ix[str(flag),'num']

def get_team_img_url(team_data,team_name):
    return r'https://www.hltv.org/galleries?team=' + team_data.ix['num',team_name]


#-------------------------------------------main---------------------------------------------


while True:
    allmonth = ['january','february','march','april','may','june','july','august','september','october','november','december']
    somemonth = ['january','february','march','april','may']
    allyear = ['2018','2017','2016','2015']
    while True:
        year = input('输入要查看的年份:')
        if year in allyear:
            break
        else:
            print('重新输入')
    while True:
        month = input('输入要查看的月份:')
        if month == '1':
            month = 'january'
        elif month == '2':
            month = 'february'
        elif month == '3':
            month = 'march'
        elif month == '4':
            month = 'april'
        elif month == '5':
            month = 'may'
        elif month == '6':
            month = 'june'
        elif month == '7':
            month = 'july'
        elif month == '8':
            month = 'august'
        elif month == '9':
            month = 'september'
        elif month == '10':
            month = 'october'
        elif month == '11':
            month = 'november'
        elif month == '12':
            month = 'december'
        else:
            print('重新输入')
            continue
        if year == '2018' :
            if month not in somemonth:
                print('数据暂时不存在，重新输入')
            else:
                break
        else:
            break
    all_day = get_ranking_day(year,month)
    while True:
        print('日期仅限输入',end = '')
        for val in all_day:
            print(val,' ',end = '')
        print()
        day = '21'
        day = input('输入要查看的日期:')
        if int(day) in all_day:
            break
        else:
            print('重新输入')
    data = get_team_data(get_ranking_soup(year,month,day))
    print('队伍排名')
    print(data.ix['position',:])
    rule = input('输入要进行的操作1.查看Team的数据2.查看用户数据统计图3.下载图片')
    if rule == '1':
        print('30Ranking Team:\n',data.ix['position',:])
        flag = 0
        while True:
            Team = input('输入队名：')
            for val in range(30):
                if Team == data.ix['name',val]:
                    get_team_base(Team,data)
                    flag = 0
                    break
                flag = 1
            if flag is 1:
                print('输入错误请重新输入')
                continue
            break
        break
    elif rule == '2':
        team_name = get_stats_team()
        print('stats Team:')
        i = 1
        for name in get_stats_team():
            if name == 'Space%20Soldiers':
                name = 'Space Soldiers'
            elif name == 'Natus%20Vincere':
                name = 'Natus Vincere' 
            elif name == 'ALTERNATE%20aTTaX':
                name = 'ALTERNATE aTTaX'
            print(i,' ',name)
            i = i+1
        flag = 0
        while True:
            Team = input('输入队名：')
            for val in range(30):
                if Team == data.ix['name',val]:
                    get_team_plot(Team,data)
                    flag = 0
                    break
                flag = 1
            if flag is 1:
                print('现未支持，或输入错误')
                continue
            break
    elif rule == '3':
        match_data = get_match_data(base_url_group)
        flag = input('输入要查看的照片类别1.Team 2.Match:')
        while True:
            _flag = 0
            if flag is '1':
                name = input('输入队伍名称:')
                for name in range(30):
                    if name == data.ix['name',name]:
                        print(get_team_img_url(data,name)) 
                        _flag = 0
                        break
                    _flag = 1
                if _flag is 1:
                    print('现未支持，或输入错误')
                    continue
                break
            elif flag is '2':
                while True:
                    print(match_data.ix[:,'match_name'])
                    _id = input('输入比赛ID:')
                    if _id >= '0' and _id <= '51':
                        print(get_match_img_url(match_data,_id))
                        break
                    else:
                        print('输入有误，重新输入')
                        continue
                break
        break

