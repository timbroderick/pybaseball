# -------------------------------
# Libraries loaded

from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
import numpy as np

from pybaseball import batting_stats_range, schedule_and_record, team_batting, team_pitching

print('ready')



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
mpl.rcParams['xtick.labelsize'] = 12
mpl.rcParams['ytick.labelsize'] = 12
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
g = sns.regplot(data=result3, x='AVGbat', y='ERA',
                fit_reg=True,
                scatter_kws={'facecolors':result3['color'],"alpha":0.6,"s":70},
                line_kws={"color":"orange","lw":1}
               )

# Set the size of the graph from here
g.figure.set_size_inches(8,8)
#plt.suptitle('Batting average vs. ERA', fontsize=16, family='Arial Black', y=.94)
plt.ylabel('ERA', fontsize=16, fontweight='bold')
plt.xlabel('BATTING AVERAGE', fontsize=16, fontweight='bold')

g.figure.savefig('static/img/BAvERA.png',bbox_inches='tight')

# -------------------------------
# Freeze the app

from flask_frozen import Freezer
from app import app, get_csv
freezer = Freezer(app)

if __name__ == '__main__':
    app.config.update(FREEZER_RELATIVE_URLS=True)
    freezer.freeze()

print('Frozen')