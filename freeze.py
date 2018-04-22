# -------------------------------
# Libraries loaded

from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
import numpy as np
import shutil

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
print('batting stats acquired')

# grab the pitching stats
pitchstats = pitching_stats(2018)
print('pitching stats acquired')


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
soxBS = pd.DataFrame( battingstats.loc[ ( battingstats["Team"] == "White Sox") ] )
soxBSselect = soxBS[['Name','AB','R','H','2B','3B','HR','RBI','BB','SO','SB','CS','AVG','OBP','SLG','wOBA','wRAA','RAR','WAR','Fld']]
soxBSselect = soxBSselect.copy()
soxBSselect.loc[:,'SOperc'] = np.round( (soxBSselect['SO'] / soxBSselect['AB'] )*100,1 )
soxBSselect['lastname'] = soxBSselect['Name'].str.split(' ').str[1]
soxBSselect.loc[:, 'AB'] = soxBSselect['AB'].astype(int)
soxBSselect.loc[:, 'R'] = soxBSselect['R'].astype(int)
soxBSselect.loc[:, 'H'] = soxBSselect['H'].astype(int)
soxBSselect.loc[:, '2B'] = soxBSselect['2B'].astype(int)
soxBSselect.loc[:, '3B'] = soxBSselect['3B'].astype(int)
soxBSselect.loc[:, 'HR'] = soxBSselect['HR'].astype(int)
soxBSselect.loc[:, 'RBI'] = soxBSselect['RBI'].astype(int)
soxBSselect.loc[:, 'BB'] = soxBSselect['BB'].astype(int)
soxBSselect.loc[:, 'SO'] = soxBSselect['SO'].astype(int)
soxBSselect.loc[:, 'SB'] = soxBSselect['SB'].astype(int)
soxBSselect.loc[:, 'CS'] = soxBSselect['CS'].astype(int)
soxBSselect = soxBSselect.rename(columns = {'2B':'dbls','3B':'trps' })
soxroster = pd.read_csv('csv/soxroster.csv', index_col=None)
left = soxBSselect
right = soxroster
soxBShit = pd.merge(left, right, how='left', left_on='Name', right_on='posName', suffixes=('_x', '_y'))
soxBShit.loc[:, 'posnum'] = soxBShit['posnum'].astype(int).astype(str)
soxBShit.to_csv("csv/soxhit.csv", index=False, encoding="utf-8")
print("Sox batting stats done")


# start Sox pitching stats 
soxPS = pd.DataFrame( pitchstats.loc[ ( pitchstats["Team"] == "White Sox") ] )
soxPSselect = soxPS[['Name','W','L','ERA','WAR','G','GS','CG','ShO','SV','BS','IP','H','R','ER','HR','BB','HBP','WP','BK','SO','IFFB','Balls','Strikes','Pitches','RS','AVG','WHIP','BABIP','FIP','WPA','RAR','K/9','BB/9','K%','BB%','LOB%','F-Strike%','FA% (pfx)','FT% (pfx)','FC% (pfx)','FS% (pfx)','FO% (pfx)','SI% (pfx)','SL% (pfx)','CU% (pfx)','KC% (pfx)','EP% (pfx)','CH% (pfx)','SC% (pfx)','KN% (pfx)','UN% (pfx)']]
soxPSselect = soxPSselect.copy()
soxPSselect = soxPSselect.rename(columns = { 'K/9':'K9','BB/9':'BB9','K%':'Kperc','BB%':'BBperc','LOB%':'LOBperc','F-Strike%':'FStrikeperc','FA% (pfx)':'FAperc','FT% (pfx)':'FTperc','FC% (pfx)':'FCperc','FS% (pfx)':'FSperc','FO% (pfx)':'FOperc','SI% (pfx)':'SIperc','SL% (pfx)':'SLperc','CU% (pfx)':'CUperc','KC% (pfx)':'KCperc','EP% (pfx)':'EPperc','CH% (pfx)':'CHperc','SC% (pfx)':'SCperc','KN% (pfx)':'KNperc','UN% (pfx)':'UNperc' })
soxPSselect['lastname'] = soxPSselect['Name'].str.split(' ').str[1]
soxPSselect.loc[:, 'W'] = soxPSselect['W'].astype(int)
soxPSselect.loc[:, 'L'] = soxPSselect['L'].astype(int)
soxPSselect.loc[:, 'G'] = soxPSselect['G'].astype(int)
soxPSselect.loc[:, 'GS'] = soxPSselect['GS'].astype(int)
soxPSselect.loc[:, 'CG'] = soxPSselect['CG'].astype(int)
soxPSselect.loc[:, 'ShO'] = soxPSselect['ShO'].astype(int)
soxPSselect.loc[:, 'SV'] = soxPSselect['SV'].astype(int)
soxPSselect.loc[:, 'BS'] = soxPSselect['BS'].astype(int)
soxPSselect.loc[:, 'avgIP'] = soxPSselect['IP'] / soxPSselect['G']
soxPSselect.loc[:, 'H'] = soxPSselect['H'].astype(int)
soxPSselect.loc[:, 'R'] = soxPSselect['R'].astype(int)
soxPSselect.loc[:, 'ER'] = soxPSselect['ER'].astype(int)
soxroster = pd.read_csv('csv/soxroster.csv', index_col=None)
left = soxPSselect
right = soxroster
soxPShit = pd.merge(left, right, how='left', left_on='Name', right_on='posName', suffixes=('_x', '_y'))
soxPShit.loc[:, 'posnum'] = soxPShit['posnum'].astype(int).astype(str)
soxPShit.to_csv("csv/soxpitch.csv", index=False, encoding="utf-8")
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

cubsBS = pd.DataFrame( battingstats.loc[ ( battingstats["Team"] == "Cubs") ] )
cubsBSselect = cubsBS[['Name','AB','R','H','2B','3B','HR','RBI','BB','SO','SB','CS','AVG','OBP','SLG','wOBA','wRAA','RAR','WAR','Fld']]
cubsBSselect = cubsBSselect.copy()
cubsBSselect.loc[:,'SOperc'] = np.round( (cubsBSselect['SO'] / cubsBSselect['AB'] )*100,1 )
cubsBSselect['lastname'] = cubsBSselect['Name'].str.split(' ').str[1]
cubsBSselect.loc[:, 'AB'] = cubsBSselect['AB'].astype(int)
cubsBSselect.loc[:, 'R'] = cubsBSselect['R'].astype(int)
cubsBSselect.loc[:, 'H'] = cubsBSselect['H'].astype(int)
cubsBSselect.loc[:, '2B'] = cubsBSselect['2B'].astype(int)
cubsBSselect.loc[:, '3B'] = cubsBSselect['3B'].astype(int)
cubsBSselect.loc[:, 'HR'] = cubsBSselect['HR'].astype(int)
cubsBSselect.loc[:, 'RBI'] = cubsBSselect['RBI'].astype(int)
cubsBSselect.loc[:, 'BB'] = cubsBSselect['BB'].astype(int)
cubsBSselect.loc[:, 'SO'] = cubsBSselect['SO'].astype(int)
cubsBSselect.loc[:, 'SB'] = cubsBSselect['SB'].astype(int)
cubsBSselect.loc[:, 'CS'] = cubsBSselect['CS'].astype(int)
cubsBSselect = cubsBSselect.rename(columns = {'2B':'dbls','3B':'trps' })
cubsroster = pd.read_csv('csv/cubsroster.csv', index_col=None)
left = cubsBSselect
right = cubsroster
cubsBShit = pd.merge(left, right, how='left', left_on='Name', right_on='posName', suffixes=('_x', '_y'))
#cubsBShit.to_csv("csv/cubshit.csv", index=False, encoding="utf-8")
cubsBShit.loc[:, 'posnum'] = cubsBShit['posnum'].astype(int).astype(str)
cubsBShit.to_csv("csv/cubshit.csv", index=False, encoding="utf-8")
print("cubs batting stats done")


# start cubs pitching stats 
cubsPS = pd.DataFrame( pitchstats.loc[ ( pitchstats["Team"] == "Cubs") ] )
cubsPSselect = cubsPS[['Name','W','L','ERA','WAR','G','GS','CG','ShO','SV','BS','IP','H','R','ER','HR','BB','HBP','WP','BK','SO','IFFB','Balls','Strikes','Pitches','RS','AVG','WHIP','BABIP','FIP','WPA','RAR','K/9','BB/9','K%','BB%','LOB%','F-Strike%','FA% (pfx)','FT% (pfx)','FC% (pfx)','FS% (pfx)','FO% (pfx)','SI% (pfx)','SL% (pfx)','CU% (pfx)','KC% (pfx)','EP% (pfx)','CH% (pfx)','SC% (pfx)','KN% (pfx)','UN% (pfx)']]
cubsPSselect = cubsPSselect.copy()
cubsPSselect = cubsPSselect.rename(columns = { 'K/9':'K9','BB/9':'BB9','K%':'Kperc','BB%':'BBperc','LOB%':'LOBperc','F-Strike%':'FStrikeperc','FA% (pfx)':'FAperc','FT% (pfx)':'FTperc','FC% (pfx)':'FCperc','FS% (pfx)':'FSperc','FO% (pfx)':'FOperc','SI% (pfx)':'SIperc','SL% (pfx)':'SLperc','CU% (pfx)':'CUperc','KC% (pfx)':'KCperc','EP% (pfx)':'EPperc','CH% (pfx)':'CHperc','SC% (pfx)':'SCperc','KN% (pfx)':'KNperc','UN% (pfx)':'UNperc' })
cubsPSselect['lastname'] = cubsPSselect['Name'].str.split(' ').str[1]
cubsPSselect.loc[:, 'W'] = cubsPSselect['W'].astype(int)
cubsPSselect.loc[:, 'L'] = cubsPSselect['L'].astype(int)
cubsPSselect.loc[:, 'G'] = cubsPSselect['G'].astype(int)
cubsPSselect.loc[:, 'GS'] = cubsPSselect['GS'].astype(int)
cubsPSselect.loc[:, 'CG'] = cubsPSselect['CG'].astype(int)
cubsPSselect.loc[:, 'ShO'] = cubsPSselect['ShO'].astype(int)
cubsPSselect.loc[:, 'SV'] = cubsPSselect['SV'].astype(int)
cubsPSselect.loc[:, 'BS'] = cubsPSselect['BS'].astype(int)
cubsPSselect.loc[:, 'avgIP'] = cubsPSselect['IP'] / cubsPSselect['G']
cubsPSselect.loc[:, 'H'] = cubsPSselect['H'].astype(int)
cubsPSselect.loc[:, 'R'] = cubsPSselect['R'].astype(int)
cubsPSselect.loc[:, 'ER'] = cubsPSselect['ER'].astype(int)
cubsroster = pd.read_csv('csv/cubsroster.csv', index_col=None)
left = cubsPSselect
right = cubsroster
cubsPSpitch = pd.merge(left, right, how='left', left_on='Name', right_on='posName', suffixes=('_x', '_y'))
#cubsPSpitch.to_csv("csv/cubspitch.csv", index=False, encoding="utf-8")
cubsPSpitch.loc[:, 'posnum'] = cubsPSpitch['posnum'].astype(int).astype(str)
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
