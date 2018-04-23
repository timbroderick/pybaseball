# -------------------------------
# Libraries loaded

from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
import numpy as np
import shutil
from pandas.io.json import json_normalize
import json

from pybaseball import schedule_and_record, team_batting, team_pitching, batting_stats, pitching_stats

print('packages loaded, ready')

import warnings
warnings.filterwarnings("ignore")

# ---------
# first remove the old directories
shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('docs', ignore_errors=True)

print('removed old build, docs folders')
#-----------
# let's grab all the information we'll need

# Scraping baseball reference for latest standings
# this scrapes the standings page
def get_soup(year):
    url = 'http://www.baseball-reference.com/leagues/MLB/{}-standings.shtml'.format(year)
    s=requests.get(url).content
    return BeautifulSoup(s, "html.parser")
# This finds all the tables and puts each of them into a dataframe
def get_tables(soup):
    tables = soup.find_all('table')
    datasets = []
    for table in tables:
        data = []
        headings = [th.get_text() for th in table.find("tr").find_all("th")]
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols.insert(0,row.find_all('a')[0]['title']) # team name
            data.append([ele for ele in cols if ele])
        datasets.append(data)
    #convert list-of-lists to dataframes
    for idx in range(len(datasets)):
        datasets[idx] = pd.DataFrame(datasets[idx])
    return datasets #returns a list of dataframes

df1 = get_soup(2018)
df2 = get_tables(df1)

print('standings info acquired')

# now scraping www.fangraphs.com for pitching and batting stats 
batting = team_batting(start_season='2018', end_season=None, league='all', ind=1)
newbat = batting[['Team','R','RBI','HR','AVG','OBP','SLG','wOBA', 'wRC+','WAR']]
newbat = newbat.rename(columns={'wRC+':'wRCplus','WAR':'WARbat','AVG':'AVGbat'})
print('team batting stats acquired')

pitching = team_pitching(start_season='2018', end_season=None, league='all', ind=1)
newpitch = pitching[['Team','ERA','SV','IP','BABIP','FIP','xFIP','WAR']]
newpitch = newpitch.rename(columns={'WAR':'WARpitch'})
print('team pitching stats acquired')

# Get data for Cubs and Sox pages
sox = schedule_and_record(2018, 'CHW')
print('Sox sched acquired')

cubs = schedule_and_record(2018, 'CHC')
print('Cubs sched acquired')

# grab the batting stats
battingstats = batting_stats(2018)
BSselect = battingstats[['Name','Team','AB','R','H','2B','3B','HR','RBI','BB','SO','SB','CS','AVG','OBP','SLG','wOBA','wRAA','RAR','WAR','Fld']]
BSselect = BSselect.copy()
BSselect.loc[:,'SOperc'] = np.round( (BSselect['SO'] / BSselect['AB'] )*100,1 )
BSselect = BSselect.rename(columns = {'2B':'dbls','3B':'trps' })
BSselect.to_csv("csv/BSselect.csv", index=False, encoding="utf-8")
print('batting stats acquired')

# grab the pitching stats
pitchstats = pitching_stats(2018)
PSselect = pitchstats[['Name','Team','W','L','ERA','WAR','G','GS','CG','ShO','SV','BS','IP','H','R','ER','HR','BB','HBP','WP','BK','SO','IFFB','Balls','Strikes','Pitches','RS','AVG','WHIP','BABIP','FIP','WPA','RAR','K/9','BB/9','K%','BB%','LOB%','F-Strike%','FA% (pfx)','FT% (pfx)','FC% (pfx)','FS% (pfx)','FO% (pfx)','SI% (pfx)','SL% (pfx)','CU% (pfx)','KC% (pfx)','EP% (pfx)','CH% (pfx)','SC% (pfx)','KN% (pfx)','UN% (pfx)']]
PSselect = PSselect.copy()
PSselect = PSselect.rename(columns = { 'K/9':'K9','BB/9':'BB9','K%':'Kperc','BB%':'BBperc','LOB%':'LOBperc','F-Strike%':'FStrikeperc','FA% (pfx)':'FAperc','FT% (pfx)':'FTperc','FC% (pfx)':'FCperc','FS% (pfx)':'FSperc','FO% (pfx)':'FOperc','SI% (pfx)':'SIperc','SL% (pfx)':'SLperc','CU% (pfx)':'CUperc','KC% (pfx)':'KCperc','EP% (pfx)':'EPperc','CH% (pfx)':'CHperc','SC% (pfx)':'SCperc','KN% (pfx)':'KNperc','UN% (pfx)':'UNperc' })
PSselect.to_csv("csv/PSselect.csv", index=False, encoding="utf-8")
print('pitching stats acquired')

#Grab the active rosters

# Getting White Sox roster
request='http://lookup-service-prod.mlb.com/json/named.roster_40.bam?team_id=145'
data= requests.get(request)
roster=data.json()
CWS=json_normalize(roster)
CWS.columns = CWS.columns.map(lambda x: x.split(".")[-1])
work = CWS['row']
df = json_normalize(work[0])
#status_code
# select only Active and DL players
notActive = ['RM']
dfWS = df[~df.status_code.isin(notActive)]
WSroster = dfWS[['name_display_first_last','jersey_number','name_last','position_txt','status_code','bats','throws']]
WSroster = WSroster.rename(columns={'name_display_first_last':'posName','jersey_number':'posnum','name_last':'lastname','position_txt':'position'})
WSroster['lastname'] = WSroster['lastname'].str.replace(r"[\"\' ]", '')
WSroster.to_csv("csv/WSroster.csv", index=False, encoding="utf-8")
print('Sox roster acquired')

# Getting Cubs roster
request='http://lookup-service-prod.mlb.com/json/named.roster_40.bam?team_id=112'
data= requests.get(request)
roster=data.json()
CHC=json_normalize(roster)
CHC.columns = CHC.columns.map(lambda x: x.split(".")[-1])
work = CHC['row']
df = json_normalize(work[0])
#status_code
# select only Active and DL players
dfCHC = df[~df.status_code.isin(notActive)]
CHCroster = dfCHC[['name_display_first_last','jersey_number','name_last','position_txt','status_code','bats','throws']]
CHCroster = CHCroster.rename(columns={'name_display_first_last':'posName','jersey_number':'posnum','name_last':'lastname','position_txt':'position'})
CHCroster['lastname'] = CHCroster['lastname'].str.replace(r"[\"\' ]", '')
CHCroster.to_csv("csv/CHCroster.csv", index=False, encoding="utf-8")
print('Cubs roster acquired')

# -------------------------------
# Create the standings file

# This grabs each dataframe, labels league and division, appends and saves csv

df_standings = pd.DataFrame()
AMeast = df2[0]
AMeast.columns = AMeast.iloc[0]
AMeast = AMeast.reindex(AMeast.index.drop(0))
df_standings = df_standings.append(AMeast)
AMcent = df2[1]
AMcent.columns = AMcent.iloc[0]
AMcent = AMcent.reindex(AMcent.index.drop(0))
df_standings = df_standings.append(AMcent)
AMwest = df2[2]
AMwest.columns = AMwest.iloc[0]
AMwest = AMwest.reindex(AMwest.index.drop(0))
df_standings = df_standings.append(AMwest)
NAeast = df2[3]
NAeast.columns = NAeast.iloc[0]
NAeast = NAeast.reindex(NAeast.index.drop(0))
df_standings = df_standings.append(NAeast)
NAcent = df2[4]
NAcent.columns = NAcent.iloc[0]
NAcent = NAcent.reindex(NAcent.index.drop(0))
df_standings = df_standings.append(NAcent)
NAwest = df2[5]
NAwest.columns = NAwest.iloc[0]
NAwest = NAwest.reindex(NAwest.index.drop(0))
df_standings = df_standings.append(NAwest)
df_standings.rename(columns={'W-L%':'WLperc'}, inplace=True)
print('standings appended')

#Joining standings with bballjoin
bballJoin = pd.read_csv('csv/bballJoin.csv', index_col=None)
left = df_standings
right = bballJoin
result = pd.merge(left, right, how='left', left_on='Tm', right_on='Tm', suffixes=('_x', '_y'))
print('1st standings join done')

# now joining batting stats
left = result
right = newbat
result2 = pd.merge(left, right, how='left', left_on='Team', right_on='Team', suffixes=('_x', '_y'))
print('batting stats joined')

# finally join pitching stats
left = result2
right = newpitch
result3 = pd.merge(left, right, how='left', left_on='Team', right_on='Team', suffixes=('_x', '_y'))
print('pitching stats joined')

result3.to_csv("csv/standings.csv", index=False, encoding="utf-8")
print('standings file done and saved')


#-------------------
# Begin creating the file for the sox standings page

soxsort = pd.DataFrame ( sox.loc[ ( sox["W/L"].notnull() ) ] )
soxsort.sort_index(ascending=False,inplace=True)
soxlast = soxsort[:1]
soxlast = soxlast.copy()
soxlast.loc[:, 'R'] = soxlast['R'].astype(int).astype(str)
soxlast.loc[:, 'RA'] = soxlast['RA'].astype(int).astype(str)
soxlast.loc[:, 'Inn'] = soxlast['Inn'].astype(int).astype(str)
soxnext = pd.DataFrame ( sox.loc[ ( sox["W/L"].isnull() ) ] )
soxnext = soxnext[:1]
soxlast = soxnext.append(soxlast)
soxlast = soxlast.rename(columns = {'Tm':'teamID', 'W/L': 'WL', 'D/N': 'DN'})
left = soxlast
right = bballJoin
soxnextlast = pd.merge(left, right, how='left', left_on='Opp', right_on='tres', suffixes=('_x', '_y'))
soxnextlast = soxnextlast.sort_values(by='R', ascending=False).reset_index(drop=True)
soxnextlast.to_csv("csv/soxnextlast.csv", index=False, encoding="utf-8")
print('Last and next sox games saved')
# Now aggregate results by team
# get df of teams played
soxteams = []
for name,grouped in soxsort.groupby(['Opp']):
    dlist = list([name])
    soxteams.append(dlist)
df = pd.DataFrame(data = soxteams, columns=['Team'])
# now aggregate results
soxlist = []
for team in df['Team']:
    # Link team in df to soxteams list in teamlist
    opp = soxsort['Opp'] == team
    df1 = soxsort[opp]
    # get wins and losses
    w = df1['W/L'] == 'W'
    wof = df1['W/L'] == 'W-wo'
    wins = len( df1[w] ) + len( df1[wof] )
    l = df1['W/L'] == 'L'
    lof = df1['W/L'] == 'L-wo'
    loses = len( df1[l] ) + len( df1[lof] )
    # average runs/against
    rAvg = np.round( df1['R'].mean() ,2)
    raAvg = np.round( df1['RA'].mean() ,2)
    # append to empty list
    slist = list([team,wins,loses,rAvg,raAvg])
    soxlist.append(slist)
# bring list into dataframe and name columns
soxagainst = pd.DataFrame(data = soxlist, columns=['teamID','Wins','Loses','AvgRuns','AvgRunsAg'])
# join aggregated list with team names
left = soxagainst
right = bballJoin
soxagg = pd.merge(left, right, how='left', left_on='teamID', right_on='tres', suffixes=('_x', '_y'))
soxagg.to_csv("csv/soxagg.csv", index=False, encoding="utf-8")
print("Sox aggregate done")


# start batting stats
left = WSroster
right = BSselect
soxBShit = pd.merge(left, right, how='left', left_on='posName', right_on='Name', suffixes=('_x', '_y'))
soxBShit = soxBShit[soxBShit.Name.notnull()]
soxBShit.loc[:, 'posnum'] = soxBShit['posnum'].astype(int).astype(str)
soxBShit.loc[:, 'AB'] = soxBShit['AB'].astype(int)
soxBShit.loc[:, 'R'] = soxBShit['R'].astype(int)
soxBShit.loc[:, 'H'] = soxBShit['H'].astype(int)
soxBShit.loc[:, 'dbls'] = soxBShit['dbls'].astype(int)
soxBShit.loc[:, 'trps'] = soxBShit['trps'].astype(int)
soxBShit.loc[:, 'HR'] = soxBShit['HR'].astype(int)
soxBShit.loc[:, 'RBI'] = soxBShit['RBI'].astype(int)
soxBShit.loc[:, 'BB'] = soxBShit['BB'].astype(int)
soxBShit.loc[:, 'SO'] = soxBShit['SO'].astype(int)
soxBShit.loc[:, 'SB'] = soxBShit['SB'].astype(int)
soxBShit.loc[:, 'CS'] = soxBShit['CS'].astype(int)
soxBShit.to_csv("csv/soxhit.csv", index=False, encoding="utf-8")
print("Sox batting stats done")


# start Sox pitching stats 
left = WSroster
right = PSselect
soxPSpitch = pd.merge(left, right, how='left', left_on='posName', right_on='Name', suffixes=('_x', '_y'))
soxPSpitch = soxPSpitch[soxPSpitch.Name.notnull()]
soxPSpitch.loc[:, 'posnum'] = soxPSpitch['posnum'].astype(int).astype(str)
soxPSpitch.loc[:, 'avgIP'] = np.round( ( soxPSpitch['IP'] / soxPSpitch['G'] ),1 )
soxPSpitch.loc[:, 'W'] = soxPSpitch['W'].astype(int)
soxPSpitch.loc[:, 'L'] = soxPSpitch['L'].astype(int)
soxPSpitch.loc[:, 'G'] = soxPSpitch['G'].astype(int)
soxPSpitch.loc[:, 'GS'] = soxPSpitch['GS'].astype(int)
soxPSpitch.loc[:, 'CG'] = soxPSpitch['CG'].astype(int)
soxPSpitch.loc[:, 'ShO'] = soxPSpitch['ShO'].astype(int)
soxPSpitch.loc[:, 'SV'] = soxPSpitch['SV'].astype(int)
soxPSpitch.loc[:, 'BS'] = soxPSpitch['BS'].astype(int)
soxPSpitch.loc[:, 'H'] = soxPSpitch['H'].astype(int)
soxPSpitch.loc[:, 'R'] = soxPSpitch['R'].astype(int)
soxPSpitch.loc[:, 'ER'] = soxPSpitch['ER'].astype(int)
soxPSpitch.loc[:, 'HR'] = soxPSpitch['HR'].astype(int)
soxPSpitch.loc[:, 'BB'] = soxPSpitch['BB'].astype(int)
soxPSpitch.loc[:, 'HBP'] = soxPSpitch['HBP'].astype(int)
soxPSpitch.loc[:, 'WP'] = soxPSpitch['WP'].astype(int)
soxPSpitch.loc[:, 'SO'] = soxPSpitch['SO'].astype(int)
soxPSpitch.loc[:, 'BK'] = soxPSpitch['BK'].astype(int)
soxPSpitch.loc[:, 'Balls'] = soxPSpitch['Balls'].astype(int)
soxPSpitch.loc[:, 'Strikes'] = soxPSpitch['Strikes'].astype(int)
soxPSpitch.loc[:, 'Pitches'] = soxPSpitch['Pitches'].astype(int)
soxPSpitch.loc[:, 'Kperc'] = np.round( (soxPSpitch['Kperc'])*100,1 )
soxPSpitch.loc[:, 'BBperc'] = np.round( (soxPSpitch['BBperc'])*100,1 )
soxPSpitch.loc[:, 'LOBperc'] = np.round( (soxPSpitch['LOBperc'])*100,1 )
soxPSpitch.loc[:, 'FStrikeperc'] = np.round( (soxPSpitch['FStrikeperc'])*100,1 )
soxPSpitch.loc[:, 'FAperc'] = np.round( (soxPSpitch['FAperc'])*100,1 )
soxPSpitch.loc[:, 'FTperc'] = np.round( (soxPSpitch['FTperc'])*100,1 )
soxPSpitch.loc[:, 'FCperc'] = np.round( (soxPSpitch['FCperc'])*100,1 )
soxPSpitch.loc[:, 'FSperc'] = np.round( (soxPSpitch['FSperc'])*100,1 )
soxPSpitch.loc[:, 'FOperc'] = np.round( (soxPSpitch['FOperc'])*100,1 )
soxPSpitch.loc[:, 'SIperc'] = np.round( (soxPSpitch['SIperc'])*100,1 )
soxPSpitch.loc[:, 'SLperc'] = np.round( (soxPSpitch['SLperc'])*100,1 )
soxPSpitch.loc[:, 'CUperc'] = np.round( (soxPSpitch['CUperc'])*100,1 )
soxPSpitch.loc[:, 'KCperc'] = np.round( (soxPSpitch['KCperc'])*100,1 )
soxPSpitch.loc[:, 'EPperc'] = np.round( (soxPSpitch['EPperc'])*100,1 )
soxPSpitch.loc[:, 'CHperc'] = np.round( (soxPSpitch['CHperc'])*100,1 )
soxPSpitch.loc[:, 'SCperc'] = np.round( (soxPSpitch['SCperc'])*100,1 )
soxPSpitch.loc[:, 'KNperc'] = np.round( (soxPSpitch['KNperc'])*100,1 )
soxPSpitch.loc[:, 'UNperc'] = np.round( (soxPSpitch['UNperc'])*100,1 )
soxPSpitch.to_csv("csv/soxpitch.csv", index=False, encoding="utf-8")
print("Sox pitching stats done")


# -------------------------------
# Start Cubs pages
cubssort = pd.DataFrame ( cubs.loc[ ( cubs["W/L"].notnull() ) ] )
cubssort.sort_index(ascending=False,inplace=True)
cubslast = cubssort[:1]
cubslast = cubslast.copy()
cubslast.loc[:, 'R'] = cubslast['R'].astype(int).astype(str)
cubslast.loc[:, 'RA'] = cubslast['RA'].astype(int).astype(str)
cubslast.loc[:, 'Inn'] = cubslast['Inn'].astype(int).astype(str)
cubsnext = pd.DataFrame ( cubs.loc[ ( cubs["W/L"].isnull() ) ] )
cubsnext = cubsnext[:1]
cubslast = cubsnext.append(cubslast)
cubslast = cubslast.rename(columns = {'Tm':'teamID', 'W/L': 'WL', 'D/N': 'DN'})
left = cubslast
right = bballJoin
cubsnextlast = pd.merge(left, right, how='left', left_on='Opp', right_on='tres', suffixes=('_x', '_y'))
cubsnextlast = cubsnextlast.sort_values(by='R', ascending=False).reset_index(drop=True)
cubsnextlast.to_csv("csv/cubsnextlast.csv", index=False, encoding="utf-8")
print('Last and next cubs games saved')
# Now aggregate results by team
# get df of teams played
cubsteams = []
for name,grouped in cubssort.groupby(['Opp']):
    dlist = list([name])
    cubsteams.append(dlist)
df = pd.DataFrame(data = cubsteams, columns=['Team'])
# now aggregate results
cubslist = []
for team in df['Team']:
    # Link team in df to cubsteams list in teamlist
    opp = cubssort['Opp'] == team
    df1 = cubssort[opp]
    # get wins and losses
    w = df1['W/L'] == 'W'
    wof = df1['W/L'] == 'W-wo'
    wins = len( df1[w] ) + len( df1[wof] )
    l = df1['W/L'] == 'L'
    lof = df1['W/L'] == 'L-wo'
    loses = len( df1[l] ) + len( df1[lof] )
    # average runs/against
    rAvg = np.round( df1['R'].mean() ,2)
    raAvg = np.round( df1['RA'].mean() ,2)
    # append to empty list
    slist = list([team,wins,loses,rAvg,raAvg])
    cubslist.append(slist)
# bring list into dataframe and name columns
cubsagainst = pd.DataFrame(data = cubslist, columns=['teamID','Wins','Loses','AvgRuns','AvgRunsAg'])
# join aggregated list with team names
left = cubsagainst
right = bballJoin
cubsagg = pd.merge(left, right, how='left', left_on='teamID', right_on='tres', suffixes=('_x', '_y'))
cubsagg.to_csv("csv/cubsagg.csv", index=False, encoding="utf-8")
print("Cubs aggregate done")


# start cubs batting stats
left = CHCroster
right = BSselect
cubsBShit = pd.merge(left, right, how='left', left_on='posName', right_on='Name', suffixes=('_x', '_y'))
cubsBShit = cubsBShit[cubsBShit.Name.notnull()]
cubsBShit.loc[:, 'posnum'] = cubsBShit['posnum'].astype(int).astype(str)
cubsBShit.loc[:, 'AB'] = cubsBShit['AB'].astype(int)
cubsBShit.loc[:, 'R'] = cubsBShit['R'].astype(int)
cubsBShit.loc[:, 'H'] = cubsBShit['H'].astype(int)
cubsBShit.loc[:, 'dbls'] = cubsBShit['dbls'].astype(int)
cubsBShit.loc[:, 'trps'] = cubsBShit['trps'].astype(int)
cubsBShit.loc[:, 'HR'] = cubsBShit['HR'].astype(int)
cubsBShit.loc[:, 'RBI'] = cubsBShit['RBI'].astype(int)
cubsBShit.loc[:, 'BB'] = cubsBShit['BB'].astype(int)
cubsBShit.loc[:, 'SO'] = cubsBShit['SO'].astype(int)
cubsBShit.loc[:, 'SB'] = cubsBShit['SB'].astype(int)
cubsBShit.loc[:, 'CS'] = cubsBShit['CS'].astype(int)
cubsBShit.to_csv("csv/cubshit.csv", index=False, encoding="utf-8")
print("cubs batting stats done")


# start cubs pitching stats 
left = CHCroster
right = PSselect
cubsPSpitch = pd.merge(left, right, how='left', left_on='posName', right_on='Name', suffixes=('_x', '_y'))
cubsPSpitch = cubsPSpitch[cubsPSpitch.Name.notnull()]
cubsPSpitch.loc[:, 'posnum'] = cubsPSpitch['posnum'].astype(int).astype(str)
cubsPSpitch.loc[:, 'avgIP'] = np.round( ( cubsPSpitch['IP'] / cubsPSpitch['G'] ),1 )
cubsPSpitch.loc[:, 'W'] = cubsPSpitch['W'].astype(int)
cubsPSpitch.loc[:, 'L'] = cubsPSpitch['L'].astype(int)
cubsPSpitch.loc[:, 'G'] = cubsPSpitch['G'].astype(int)
cubsPSpitch.loc[:, 'GS'] = cubsPSpitch['GS'].astype(int)
cubsPSpitch.loc[:, 'CG'] = cubsPSpitch['CG'].astype(int)
cubsPSpitch.loc[:, 'ShO'] = cubsPSpitch['ShO'].astype(int)
cubsPSpitch.loc[:, 'SV'] = cubsPSpitch['SV'].astype(int)
cubsPSpitch.loc[:, 'BS'] = cubsPSpitch['BS'].astype(int)
cubsPSpitch.loc[:, 'H'] = cubsPSpitch['H'].astype(int)
cubsPSpitch.loc[:, 'R'] = cubsPSpitch['R'].astype(int)
cubsPSpitch.loc[:, 'ER'] = cubsPSpitch['ER'].astype(int)
cubsPSpitch.loc[:, 'HR'] = cubsPSpitch['HR'].astype(int)
cubsPSpitch.loc[:, 'BB'] = cubsPSpitch['BB'].astype(int)
cubsPSpitch.loc[:, 'HBP'] = cubsPSpitch['HBP'].astype(int)
cubsPSpitch.loc[:, 'WP'] = cubsPSpitch['WP'].astype(int)
cubsPSpitch.loc[:, 'BK'] = cubsPSpitch['BK'].astype(int)
cubsPSpitch.loc[:, 'SO'] = cubsPSpitch['SO'].astype(int)
cubsPSpitch.loc[:, 'Balls'] = cubsPSpitch['Balls'].astype(int)
cubsPSpitch.loc[:, 'Strikes'] = cubsPSpitch['Strikes'].astype(int)
cubsPSpitch.loc[:, 'Pitches'] = cubsPSpitch['Pitches'].astype(int)
cubsPSpitch.loc[:, 'Kperc'] = np.round( (cubsPSpitch['Kperc'])*100,1 )
cubsPSpitch.loc[:, 'BBperc'] = np.round( (cubsPSpitch['BBperc'])*100,1 )
cubsPSpitch.loc[:, 'LOBperc'] = np.round( (cubsPSpitch['LOBperc'])*100,1 )
cubsPSpitch.loc[:, 'FStrikeperc'] = np.round( (cubsPSpitch['FStrikeperc'])*100,1 )
cubsPSpitch.loc[:, 'FAperc'] = np.round( (cubsPSpitch['FAperc'])*100,1 )
cubsPSpitch.loc[:, 'FTperc'] = np.round( (cubsPSpitch['FTperc'])*100,1 )
cubsPSpitch.loc[:, 'FCperc'] = np.round( (cubsPSpitch['FCperc'])*100,1 )
cubsPSpitch.loc[:, 'FSperc'] = np.round( (cubsPSpitch['FSperc'])*100,1 )
cubsPSpitch.loc[:, 'FOperc'] = np.round( (cubsPSpitch['FOperc'])*100,1 )
cubsPSpitch.loc[:, 'SIperc'] = np.round( (cubsPSpitch['SIperc'])*100,1 )
cubsPSpitch.loc[:, 'SLperc'] = np.round( (cubsPSpitch['SLperc'])*100,1 )
cubsPSpitch.loc[:, 'CUperc'] = np.round( (cubsPSpitch['CUperc'])*100,1 )
cubsPSpitch.loc[:, 'KCperc'] = np.round( (cubsPSpitch['KCperc'])*100,1 )
cubsPSpitch.loc[:, 'EPperc'] = np.round( (cubsPSpitch['EPperc'])*100,1 )
cubsPSpitch.loc[:, 'CHperc'] = np.round( (cubsPSpitch['CHperc'])*100,1 )
cubsPSpitch.loc[:, 'SCperc'] = np.round( (cubsPSpitch['SCperc'])*100,1 )
cubsPSpitch.loc[:, 'KNperc'] = np.round( (cubsPSpitch['KNperc'])*100,1 )
cubsPSpitch.loc[:, 'UNperc'] = np.round( (cubsPSpitch['UNperc'])*100,1 )
cubsPSpitch.to_csv("csv/cubspitch.csv", index=False, encoding="utf-8")
print("cubs pitching stats done")


# ----------------------
# Begin charting
print('begin Seaborn charting')

# -------------------------------
# load what we need for the visuals

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import ticker
import math

#-----
# set styles

mpl.rcParams['font.family'] = ['sans-serif']
mpl.rcParams['xtick.labelsize'] = 17
mpl.rcParams['ytick.labelsize'] = 17
mpl.rcParams['lines.linewidth'] = 0.75

mpl.rcParams['pdf.fonttype'] = 42 # allegedly allows text to be saved as editable

mpl.rcParams['font.sans-serif'] = ['Arial Narrow']
mpl.rcParams['font.size'] = 9
mpl.rcParams['text.usetex'] = False
mpl.rcParams['svg.fonttype'] = 'none'

plt.style.use(['ggplot'])

from scipy.stats import norm

print('plotting ready')

# ERA vs Batting average
plt.figure()
g = sns.regplot(data=result3, x='AVGbat', y='ERA',
                fit_reg=True,
                scatter_kws={'facecolors':result3['color'],"alpha":0.6,"s":70,'edgecolor':'none'},
                line_kws={"color":"orange","lw":1}
               )
g.figure.set_size_inches(8,8)
plt.ylabel('ERA', fontsize=16, fontweight='bold')
plt.xlabel('BATTING AVERAGE', fontsize=16, fontweight='bold')
g.figure.savefig('static/img/BAvERA.png',bbox_inches='tight')


# WAR stats
plt.figure()
g = sns.regplot(data=result3, x='WARbat', y='WARpitch',
                fit_reg=True,
                scatter_kws={'facecolors':result3['color'],"alpha":0.6,"s":70,'edgecolor':'none'},
                line_kws={"color":"orange","lw":1}
               )
g.figure.set_size_inches(8,8)
plt.ylabel('WAR PITCHING', fontsize=16, fontweight='bold')
plt.xlabel('WAR BATTING', fontsize=16, fontweight='bold')
g.figure.savefig('static/img/WAR.png',bbox_inches='tight')

# offense stats
plt.figure()
g = sns.regplot(data=result3, x='wOBA', y='RBI',
                fit_reg=True,
                scatter_kws={'facecolors':result3['color'],"alpha":0.6,"s":70,'edgecolor':'none'},
                line_kws={"color":"orange","lw":1}
               )

g.figure.set_size_inches(8,8)
plt.ylabel('RBI', fontsize=16, fontweight='bold')
plt.xlabel('Weighted On-Base Average', fontsize=16, fontweight='bold')
g.figure.savefig('static/img/offense.png',bbox_inches='tight')

# defense stats
plt.figure()
g = sns.regplot(data=result3, x='BABIP', y='FIP',
                fit_reg=True,
                scatter_kws={'facecolors':result3['color'],"alpha":0.6,"s":70,'edgecolor':'none'},
                line_kws={"color":"orange","lw":1}
               )
g.figure.set_size_inches(8,8)
plt.ylabel('Fielding Independent Pitching', fontsize=16, fontweight='bold')
plt.xlabel('Batting Average on Balls In Play', fontsize=16, fontweight='bold')
g.figure.savefig('static/img/defense.png',bbox_inches='tight')

# bar plot, start with sorting
# need to reset the index
dfHR = result3.sort_values(by='HR', ascending=False).reset_index(drop=True)
# clear the plt figure
plt.figure()
my_dpi=150
plt.xlim(0, 300)
g = sns.barplot(
    x='HR',
    y='Team',
    data=dfHR,
    palette=dfHR['color']
)
plt.plot([264, 264], [-10, 30], linewidth=1)
g.figure.set_size_inches(8,14)
g.set_ylabel('TEAM', fontsize=16, fontweight='bold')
g.set_xlabel('HOME RUNS', fontsize=16, fontweight='bold')
# placing the bar labels
for p in g.patches:
    width = math.ceil( p.get_width() )
    g.text(width*1.04, p.get_y() + p.get_height()/1.25,
            "{:" ">6}".format( width ),
            fontsize=15, color="black", fontweight='bold', zorder=10)
g.figure.savefig('static/img/HR.png',bbox_inches='tight')

print("p1 charts created")


# begin Sox hitting charts

for index, row in soxBShit.iterrows():
    d = {'hits': ['WALKS','SO','HITS','1B', '2B', '3B', 'HR']}
    df = pd.DataFrame(data=d)
    df['hitperc'] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    df['hitcolor'] = ['#000000','#000000','#000000','#AAAAAA','#AAAAAA','#AAAAAA','#AAAAAA']
    if ( row.H == 0):
        junkvar = []
    else:
        df['hitperc'][0] = np.round( (row.BB / row.AB)*100,1 )
        df['hitperc'][1] = np.round( (row.SO / row.AB)*100,1 )
        df['hitperc'][2] = np.round( (row.H / row.AB)*100,1 )
        onebs = row.H - ( row.dbls + row.trps + row.HR )
        df['hitperc'][3] = np.round( (onebs / row.H)*100,1 )
        df['hitperc'][4] = np.round( (row.dbls / row.H)*100,1 )
        df['hitperc'][5] = np.round( (row.trps / row.H)*100,1 )
        df['hitperc'][6] = np.round( (row.HR / row.H)*100,1 )
    # start the plot
    plt.figure()
    my_dpi=150
    plt.ylim(0, 100)
    tick_locator = ticker.MaxNLocator(10)
    g = sns.barplot(
        x='hits',
        y='hitperc',
        data=df,
        palette=df['hitcolor']
    )
    g.yaxis.set_major_locator(tick_locator)
    g.grid(axis='y', linewidth=2)
    g.figure.set_size_inches(8,6)
    plt.plot([2.5, 2.5], [0, 100], linewidth=2)
    # Add labels to the plot
    style = dict(fontsize=18, family='Arial', fontweight='bold', color='black')
    plt.text(0, 89, "As % of AB", **style)
    plt.text(3, 89, "As % of hits", **style)
    g.set_ylabel('% of AT BATS | HITS', fontsize=16, fontweight='bold')
    g.set_xlabel('AT-BAT RESULTS | HIT TYPE', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/sox' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight')
print('Sox hitting charts done')

# start Sox pitching charts

# begin Sox hitting charts

for index, row in soxPSpitch.iterrows():
    d = {'pitches': ['FASTBALL','FS-2SEAM','CUTTER','SPLIT-FINGER','FORKBALL', 'SINKER', 'SLIDER', 'CURVEBALL','EPHESUS','CHANGE-UP','SCREWBALL','KNUCKLEBALL','KNUCKLE-CURVE','UNKNOWN']}
    df = pd.DataFrame(data=d)
    df['perc'] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    if ( row.Pitches == 0):
        junkvar = []
    else:
        df['perc'][0] = row.FAperc
        df['perc'][1] = row.FTperc
        df['perc'][2] = row.FCperc
        df['perc'][3] = row.FSperc
        df['perc'][4] = row.FOperc
        df['perc'][5] = row.SIperc
        df['perc'][6] = row.SLperc
        df['perc'][7] = row.CUperc
        df['perc'][8] = row.EPperc
        df['perc'][9] = row.CHperc
        df['perc'][10] = row.SCperc
        df['perc'][11] = row.KNperc
        df['perc'][12] = row.KCperc
        df['perc'][13] = row.UNperc

    df = df.fillna(value=0)
    # start the plot
    plt.figure()
    my_dpi=150
    plt.xlim(0, 100)
    from matplotlib import ticker
    tick_locator = ticker.MaxNLocator(10)
    g = sns.barplot(
        x='perc',
        y='pitches',
        data=df,
        color="black"
    )
    g.xaxis.set_major_locator(tick_locator)
    g.grid(axis='x', linewidth=2)
    g.figure.set_size_inches(6,6)
    g.set_xlabel('PERCENT THROWN', fontsize=16, fontweight='bold')
    g.set_ylabel('PITCH TYPE', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/soxpitch' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight')
print('Sox pitching charts done')

# start cubs hitting charts

for index, row in cubsBShit.iterrows():
    d = {'hits': ['WALKS','SO','HITS','1B', '2B', '3B', 'HR']}
    df = pd.DataFrame(data=d)
    df['hitperc'] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    df['hitcolor'] = ['#000FFF','#000FFF','#000FFF','#737AFF','#737AFF','#737AFF','#737AFF']
    if ( row.H == 0):
        junkvar = []
    else:
        df['hitperc'][0] = np.round( (row.BB / row.AB)*100,1 )
        df['hitperc'][1] = np.round( (row.SO / row.AB)*100,1 )
        df['hitperc'][2] = np.round( (row.H / row.AB)*100,1 )
        onebs = row.H - ( row.dbls + row.trps + row.HR )
        df['hitperc'][3] = np.round( (onebs / row.H)*100,1 )
        df['hitperc'][4] = np.round( (row.dbls / row.H)*100,1 )
        df['hitperc'][5] = np.round( (row.trps / row.H)*100,1 )
        df['hitperc'][6] = np.round( (row.HR / row.H)*100,1 )
    # start the plot
    plt.figure()
    my_dpi=150
    plt.ylim(0, 100)
    tick_locator = ticker.MaxNLocator(10)
    g = sns.barplot(
        x='hits',
        y='hitperc',
        data=df,
        palette=df['hitcolor']
    )
    g.yaxis.set_major_locator(tick_locator)
    g.grid(axis='y', linewidth=2)
    g.figure.set_size_inches(8,6)
    plt.plot([2.5, 2.5], [0, 100], linewidth=2)
    # Add labels to the plot
    style = dict(fontsize=18, family='Arial', fontweight='bold', color='black')
    plt.text(0, 89, "As % of AB", **style)
    plt.text(3, 89, "As % of hits", **style)
    g.set_ylabel('% of AT BATS | HITS', fontsize=16, fontweight='bold')
    g.set_xlabel('AT-BAT RESULTS | HIT TYPE', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/cubs' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight')

print('cubs hitting charts done')


# begin Cubs hitting charts

for index, row in cubsPSpitch.iterrows():
    d = {'pitches': ['FASTBALL','FS-2SEAM','CUTTER','SPLIT-FINGER','FORKBALL', 'SINKER', 'SLIDER', 'CURVEBALL','EPHESUS','CHANGE-UP','SCREWBALL','KNUCKLEBALL','KNUCKLE-CURVE','UNKNOWN']}
    df = pd.DataFrame(data=d)
    df['perc'] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    if ( row.Pitches == 0):
        junkvar = []
    else:
        df['perc'][0] = row.FAperc
        df['perc'][1] = row.FTperc
        df['perc'][2] = row.FCperc
        df['perc'][3] = row.FSperc
        df['perc'][4] = row.FOperc
        df['perc'][5] = row.SIperc
        df['perc'][6] = row.SLperc
        df['perc'][7] = row.CUperc
        df['perc'][8] = row.EPperc
        df['perc'][9] = row.CHperc
        df['perc'][10] = row.SCperc
        df['perc'][11] = row.KNperc
        df['perc'][12] = row.KCperc
        df['perc'][13] = row.UNperc

    df = df.fillna(value=0)
    # start the plot
    plt.figure()
    my_dpi=150
    plt.xlim(0, 100)
    from matplotlib import ticker
    tick_locator = ticker.MaxNLocator(10)
    g = sns.barplot(
        x='perc',
        y='pitches',
        data=df,
        color="#000FFF"
    )
    g.xaxis.set_major_locator(tick_locator)
    g.grid(axis='x', linewidth=2)
    g.figure.set_size_inches(6,6)
    g.set_xlabel('PERCENT THROWN', fontsize=16, fontweight='bold')
    g.set_ylabel('PITCH TYPE', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/cubspitch' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight')
print('Cubs pitching charts done')





# -------------------------------
# Freeze the app

from flask_frozen import Freezer
from app import app, get_csv
freezer = Freezer(app)

if __name__ == '__main__':
    app.config.update(FREEZER_RELATIVE_URLS=True)
    freezer.freeze()

print('Frozen')

# Now rename the build directory

shutil.move('build', 'docs')

print('all done')
