# -------------------------------
# Libraries loaded

from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd
import numpy as np

from pybaseball import batting_stats_range, schedule_and_record

print('ready')



# -------------------------------
# Get the standings


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

AMeast = df2[0]
AMeast.columns = AMeast.iloc[0]
AMeast = AMeast.reindex(AMeast.index.drop(0))
AMeast['League'] = 'American'
AMeast['Division'] = 'East'
AMcent = df2[1]
AMcent.columns = AMcent.iloc[0]
AMcent = AMcent.reindex(AMcent.index.drop(0))
AMcent['League'] = 'American'
AMcent['Division'] = 'Central'
AMwest = df2[2]
AMwest.columns = AMwest.iloc[0]
AMwest = AMwest.reindex(AMwest.index.drop(0))
AMwest['League'] = 'American'
AMwest['Division'] = 'West'
NAeast = df2[3]
NAeast.columns = NAeast.iloc[0]
NAeast = NAeast.reindex(NAeast.index.drop(0))
NAeast['League'] = 'National'
NAeast['Division'] = 'East'
NAcent = df2[4]
NAcent.columns = NAcent.iloc[0]
NAcent = NAcent.reindex(NAcent.index.drop(0))
NAcent['League'] = 'National'
NAcent['Division'] = 'Central'
NAwest = df2[5]
NAwest.columns = NAwest.iloc[0]
NAwest = NAwest.reindex(NAwest.index.drop(0))
NAwest['League'] = 'National'
NAwest['Division'] = 'West'

df_standings = pd.DataFrame()
df_standings = df_standings.append(AMeast)
df_standings = df_standings.append(AMcent)
df_standings = df_standings.append(AMwest)
df_standings = df_standings.append(NAeast)
df_standings = df_standings.append(NAcent)
df_standings = df_standings.append(NAwest)
df_standings.rename(columns={'W-L%':'WLperc'}, inplace=True)
df_standings.to_csv("csv/standings.csv", index=False, encoding="utf-8")

print('standings file done')



# -------------------------------
# Freeze the app

from flask_frozen import Freezer
from app import app, get_csv
freezer = Freezer(app)

if __name__ == '__main__':
    app.config.update(FREEZER_RELATIVE_URLS=True)
    freezer.freeze()

print('Frozen')