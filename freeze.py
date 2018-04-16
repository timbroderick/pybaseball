# -------------------------------
# Libraries loaded

from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
import numpy as np
import shutil

from pybaseball import batting_stats_range, schedule_and_record, team_batting, team_pitching

print('ready')

import warnings
warnings.filterwarnings("ignore")

# ---------
# first remove the old directories
shutil.rmtree('build', ignore_errors=True)
shutil.rmtree('docs', ignore_errors=True)

# -------------------------------
# Create the standings file


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

print('tables gotten')

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

# now scraping www.fangraphs.com for pitching and batting stats 

batting = team_batting(start_season='2018', end_season=None, league='all', ind=1)
newbat = batting[['Team','R','RBI','HR','AVG','OBP','SLG','wOBA', 'wRC+','WAR']]
newbat = newbat.rename(columns={'wRC+':'wRCplus','WAR':'WARbat','AVG':'AVGbat'})

print('batting stats done')

pitching = team_pitching(start_season='2018', end_season=None, league='all', ind=1)
newpitch = pitching[['Team','ERA','SV','IP','BABIP','FIP','xFIP','WAR']]
newpitch = newpitch.rename(columns={'WAR':'WARpitch'})

print('pitching stats done')

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



# -------------------------------
# Now we're going to create the visuals

import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
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


print("charts created")



# -------------------------------
# Get data for Sox page

print('Get Sox sched stuff')
sox = schedule_and_record(2018, 'CHW')
soxsort = pd.DataFrame ( sox.loc[ ( sox["W/L"].notnull() ) ] )
soxsort.sort_index(ascending=False,inplace=True)
soxlast = soxsort[:1]
soxlast = soxlast.copy()
soxlast.loc[:, 'R'] = soxlast['R'].astype(int)
soxlast.loc[:, 'R'] = soxlast['R'].astype(str)
soxlast.loc[:, 'RA'] = soxlast['RA'].astype(int)
soxlast.loc[:, 'RA'] = soxlast['RA'].astype(str)
soxlast.loc[:, 'Inn'] = soxlast['Inn'].astype(int)
soxlast.loc[:, 'Inn'] = soxlast['Inn'].astype(str)
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
    wins = len( df1[w] )
    l = df1['W/L'] == 'L'
    loses = len( df1[l] )
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


# -------------------------------
# Get data for cubs page

print('Get cubs sched stuff')
cubs = schedule_and_record(2018, 'CHC')
cubssort = pd.DataFrame ( cubs.loc[ ( cubs["W/L"].notnull() ) ] )
cubssort.sort_index(ascending=False,inplace=True)
cubslast = cubssort[:1]
cubslast = cubslast.copy()
cubslast.loc[:, 'R'] = cubslast['R'].astype(int)
cubslast.loc[:, 'R'] = cubslast['R'].astype(str)
cubslast.loc[:, 'RA'] = cubslast['RA'].astype(int)
cubslast.loc[:, 'RA'] = cubslast['RA'].astype(str)
cubslast.loc[:, 'Inn'] = cubslast['Inn'].astype(int)
cubslast.loc[:, 'Inn'] = cubslast['Inn'].astype(str)
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
    wins = len( df1[w] )
    l = df1['W/L'] == 'L'
    loses = len( df1[l] )
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
