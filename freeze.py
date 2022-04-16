import pandas as pd

import warnings
warnings.filterwarnings("ignore")

taskdata = {'task': ['Packages loaded','old directories removed','standings','team batting','team pitching','Sox sched','Cubs sched','batting stats','pitching stats','Sox roster','Cubs roster','stadings appended','standings joined','batting stats joined','pitching stats joined','Sox games','Sox players','Sox batting','Sox pitching','Cubs games','Cubs players','Cubs batting','Cubs pitching','Plotting','League plots','Sox hitting charts','Sox pitching charts','Cubs hitting charts','Cubs pitching charts','h2h batting stats','h2h batting charts','h2h pitching stats','h2h pitching charts','site frozen','pushed to web']}
xreport = pd.DataFrame(data=taskdata)
xreport ['status'] = ['Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem']

get_season = 2022
int_season ='2022'
print('getting the ',get_season,' season')

try:
    # -------------------------------
    # Libraries loaded

    import requests
    import datetime
    import numpy as np
    import shutil
    from pandas.io.json import json_normalize
    import json

    from pybaseball import schedule_and_record, team_batting, team_pitching, batting_stats, pitching_stats, standings

    # packages
    xreport.loc[0, 'status'] = 'OK'
    print('packages loaded, ready')


    # ---------
    # first remove the old directories
    shutil.rmtree('build', ignore_errors=True)
    shutil.rmtree('docs', ignore_errors=True)

    # old directories removed
    xreport.loc[1, 'status'] = 'OK'
    print('removed old build, docs folders')
    #-----------
    # let's grab all the information we'll need

    # get the standings, new method

    dfstand = standings(get_season)
    getthis = '1'

    df_standings = pd.DataFrame()
    for d in dfstand:
        #print(type(d))
        d = pd.DataFrame(d)
        df_standings=df_standings.append(d)
    df_standings.rename(columns={'W-L%':'WLperc'}, inplace=True)
    df_standings.to_csv("csv/standingstest.csv", index=False, encoding="utf-8")

    # standings
    xreport.loc[2, 'status'] = 'OK'
    print('standings info acquired')

    # now scraping www.fangraphs.com for pitching and batting stats
    batting = team_batting(start_season=get_season, end_season=None, league='all', ind=1)
    newbat = batting[['Team','R','RBI','HR','AVG','OBP','SLG','wOBA', 'wRC+','WAR']]
    newbat = newbat.rename(columns={'wRC+':'wRCplus','WAR':'WARbat','AVG':'AVGbat'})
    # team batting
    xreport.loc[3, 'status'] = 'OK'
    print('team batting stats acquired')

    pitching = team_pitching(start_season=get_season, end_season=None, league='all', ind=1)
    newpitch = pitching[['Team','ERA','SV','IP','BABIP','FIP','xFIP','WAR']]
    newpitch = newpitch.rename(columns={'WAR':'WARpitch'})
    # team pitching
    xreport.loc[4, 'status'] = 'OK'
    print('team pitching stats acquired')

    # Get data for Cubs and Sox pages
    sox = schedule_and_record(get_season, 'CHW')
    # Sox sched
    xreport.loc[5, 'status'] = 'OK'
    print('Sox sched acquired')
    sox.to_csv("csv/soxrecord.csv", index=False, encoding="utf-8")

    cubs = schedule_and_record(get_season, 'CHC')
    # Cubs sched
    xreport.loc[6, 'status'] = 'OK'
    print('Cubs sched acquired')
    cubs.to_csv("csv/cubsrecord.csv", index=False, encoding="utf-8")

    # grab the batting stats
    battingstats = batting_stats(get_season,qual=1)
    BSselect = battingstats[['Name','Team','PA','AB','R','H','2B','3B','HR','RBI','BB','SO','SB','CS','AVG','OBP','SLG','wOBA','wRAA','RAR','WAR','Fld']]
    BSselect = BSselect.copy()
    BSselect.loc[:,'SOperc'] = np.round( (BSselect['SO'] / BSselect['AB'] )*100,1 )
    BSselect = BSselect.rename(columns = {'2B':'dbls','3B':'trps' })
    BSselect.to_csv("csv/BSselect.csv", index=False, encoding="utf-8")
    # batting stats
    xreport.loc[7, 'status'] = 'OK'
    print('batting stats acquired')

    # grab the pitching stats
    pitchstats = pitching_stats(get_season,qual=1)
    PSselect = pitchstats[['Name','Team','W','L','ERA','WAR','G','GS','CG','ShO','SV','BS','IP','H','R','ER','HR','BB','HBP','WP','BK','SO','IFFB','Balls','Strikes','Pitches','RS','AVG','WHIP','BABIP','FIP','WPA','RAR','K/9','BB/9','K%','BB%','LOB%','F-Strike%','FA% (sc)','FT% (sc)','FC% (sc)','FS% (sc)','FO% (sc)','SI% (sc)','SL% (sc)','CU% (sc)','KC% (sc)','EP% (sc)','CH% (sc)','SC% (sc)','KN% (sc)','UN% (sc)']]
    PSselect = PSselect.copy()
    PSselect = PSselect.rename(columns = { 'K/9':'K9','BB/9':'BB9','K%':'Kperc','BB%':'BBperc','LOB%':'LOBperc','F-Strike%':'FStrikeperc','FA% (sc)':'FAperc','FT% (sc)':'FTperc','FC% (sc)':'FCperc','FS% (sc)':'FSperc','FO% (sc)':'FOperc','SI% (sc)':'SIperc','SL% (sc)':'SLperc','CU% (sc)':'CUperc','KC% (sc)':'KCperc','EP% (sc)':'EPperc','CH% (sc)':'CHperc','SC% (sc)':'SCperc','KN% (sc)':'KNperc','UN% (sc)':'UNperc' })
    PSselect.to_csv("csv/PSselect.csv", index=False, encoding="utf-8")
    # pitching stats
    xreport.loc[8, 'status'] = 'OK'
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
    # Sox roster
    xreport.loc[9, 'status'] = 'OK'
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
    # Cubs roster
    xreport.loc[10, 'status'] = 'OK'
    print('Cubs roster acquired')

    # -------------------------------
    # Create the standings file

    xreport.loc[11, 'status'] = 'OK'
    print('standings appended')

    #Joining standings with bballjoin
    bballJoin = pd.read_csv('csv/bballJoin.csv', index_col=None)
    left = df_standings
    right = bballJoin
    result = pd.merge(left, right, how='left', left_on='Tm', right_on='Tm', suffixes=('_x', '_y'))
    # standings joined
    result.to_csv("csv/result.csv", index=False, encoding="utf-8")

    xreport.loc[12, 'status'] = 'OK'
    print('1st standings join done')

    # now joining batting stats
    left = result
    right = newbat
    result2 = pd.merge(left, right, how='left', left_on='tres', right_on='Team', suffixes=('_x', '_y'))
    newbat.to_csv("csv/newbat.csv", index=False, encoding="utf-8")
    result2.to_csv("csv/result2.csv", index=False, encoding="utf-8")

    # batting stats joined
    xreport.loc[13, 'status'] = 'OK'
    print('batting stats joined')

    # finally join pitching stats
    left = result2
    right = newpitch
    result3 = pd.merge(left, right, how='left', left_on='tres', right_on='Team', suffixes=('_x', '_y'))
    print('pitching stats joined')
    result3.to_csv("csv/standings.csv", index=False, encoding="utf-8")
    print('standings file done and saved')
    # pitching stats joined and standings file saved
    xreport.loc[14, 'status'] = 'OK'


    #-------------------
    # Begin creating the file for the sox standings page

    soxsort = pd.DataFrame ( sox.loc[ ( sox["W/L"].notnull() ) ] )
    soxsort.sort_index(ascending=False,inplace=True)
    soxlast = soxsort[:2]
    soxlast = soxlast.copy().reset_index(drop=True)
    soxlast.loc[:, 'R'] = soxlast['R'].astype(int).astype(str)
    soxlast.loc[:, 'RA'] = soxlast['RA'].astype(int).astype(str)
    soxlast.loc[:, 'Inn'] = soxlast['Inn'].astype(int).astype(str)
    soxlast.loc[:, 'sorting'] = 0
    soxlast.loc[0, 'sorting'] = 0
    soxlast.loc[1, 'sorting'] = 1
    soxnext = pd.DataFrame ( sox.loc[ ( sox["W/L"].isnull() ) ] )
    soxnext = soxnext[:2].reset_index(drop=True)
    soxnext.loc[:, 'sorting'] = 0
    soxnext.loc[0, 'sorting'] = 2
    soxnext.loc[1, 'sorting'] = 3
    soxlast = soxnext.append(soxlast)
    soxlast = soxlast.rename(columns = {'Tm':'teamID', 'W/L': 'WL', 'D/N': 'DN'})
    left = soxlast
    right = bballJoin
    soxnextlast = pd.merge(left, right, how='left', left_on='Opp', right_on='tres', suffixes=('_x', '_y'))
    soxnextlast = soxnextlast.sort_values(by='sorting', ascending=True).reset_index(drop=True)
    soxnextlast['Date'] = soxnextlast['Date'].str.replace( r"\(.*\)","" )
    soxnextlast.to_csv("csv/soxnextlast.csv", index=False, encoding="utf-8")
    # Sox games
    xreport.loc[15, 'status'] = 'OK'
    print('Last and next sox games saved')

    # Now aggregate results by team
    # get df of teams played

    soxteams = []
    for name,grouped in soxsort.groupby(['Opp']):
        dlist = name
        soxteams.append(dlist)

    soxlist = []
    for team in soxteams:
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
        slist = [team,wins,loses,rAvg,raAvg]
        soxlist.append(slist)


    # bring list into dataframe and name columns
    soxagainst = pd.DataFrame(data = soxlist, columns=['teamID','Wins','Loses','AvgRuns','AvgRunsAg'])
    # join aggregated list with team names
    left = soxagainst
    right = bballJoin
    soxagg = pd.merge(left, right, how='left', left_on='teamID', right_on='tres', suffixes=('_x', '_y'))
    soxagg.to_csv("csv/soxagg.csv", index=False, encoding="utf-8")
    # Sox players
    xreport.loc[16, 'status'] = 'OK'
    print("Sox aggregate done")




    # start batting stats
    left = WSroster
    right = BSselect
    soxBShit = pd.merge(left, right, how='left', left_on='posName', right_on='Name', suffixes=('_x', '_y'))
    soxBShit = soxBShit[soxBShit.Name.notnull()]
    soxBShit.loc[:, 'posnum'] = soxBShit['posnum'].astype(int).astype(str)
    soxBShit.loc[:, 'PA'] = soxBShit['PA'].astype(int)
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
    # Sox batting
    xreport.loc[17, 'status'] = 'OK'
    print("Sox batting stats done")



    # start Sox pitching stats
    left = WSroster
    right = PSselect
    soxPSpitch = pd.merge(left, right, how='left', left_on='posName', right_on='Name', suffixes=('_x', '_y'))
    soxPSpitch.to_csv("csv/test1.csv", index=False, encoding="utf-8")
    soxPSpitch = soxPSpitch[soxPSpitch.Name.notnull()]
    soxPSpitch.to_csv("csv/test2.csv", index=False, encoding="utf-8")
    soxPSpitch = soxPSpitch[soxPSpitch.lastname != "Fulmer"]
    soxPSpitch.to_csv("csv/test3.csv", index=False, encoding="utf-8")
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
    # Sox pitching
    xreport.loc[18, 'status'] = 'OK'
    print("Sox pitching stats done")

    # -------------------------------
    # Start Cubs pages
    cubssort = pd.DataFrame ( cubs.loc[ ( cubs["W/L"].notnull() ) ] )
    cubssort.sort_index(ascending=False,inplace=True)
    cubslast = cubssort[:2]
    cubslast = cubslast.copy().reset_index(drop=True)
    cubslast.loc[:, 'R'] = cubslast['R'].astype(int).astype(str)
    cubslast.loc[:, 'RA'] = cubslast['RA'].astype(int).astype(str)
    cubslast.loc[:, 'Inn'] = cubslast['Inn'].astype(int).astype(str)
    cubslast.loc[:, 'sorting'] = 0
    cubslast.loc[0, 'sorting'] = 0
    cubslast.loc[1, 'sorting'] = 1
    cubsnext = pd.DataFrame ( cubs.loc[ ( cubs["W/L"].isnull() ) ] )
    cubsnext = cubsnext[:2].reset_index(drop=True)
    cubsnext.loc[:, 'sorting'] = 0
    cubsnext.loc[0, 'sorting'] = 2
    cubsnext.loc[1, 'sorting'] = 3
    cubslast = cubsnext.append(cubslast)
    cubslast = cubslast.rename(columns = {'Tm':'teamID', 'W/L': 'WL', 'D/N': 'DN'})
    left = cubslast
    right = bballJoin
    cubsnextlast = pd.merge(left, right, how='left', left_on='Opp', right_on='tres', suffixes=('_x', '_y'))
    cubsnextlast = cubsnextlast.sort_values(by='sorting', ascending=True).reset_index(drop=True)
    cubsnextlast['Date'] = cubsnextlast['Date'].str.replace( r"\(.*\)","" )
    cubsnextlast.to_csv("csv/cubsnextlast.csv", index=False, encoding="utf-8")
    # Cubs games
    xreport.loc[19, 'status'] = 'OK'
    print('Last and next cubs games saved')


    # Now aggregate results by team
    # get df of teams played
    cubsteams = []
    for name,grouped in cubssort.groupby(['Opp']):
        dlist = name
        cubsteams.append(dlist)
    # now aggregate results
    cubslist = []
    for team in cubsteams:
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
        slist = [team,wins,loses,rAvg,raAvg]
        cubslist.append(slist)
    # bring list into dataframe and name columns
    cubsagainst = pd.DataFrame(data = cubslist, columns=['teamID','Wins','Loses','AvgRuns','AvgRunsAg'])
    # join aggregated list with team names
    left = cubsagainst
    right = bballJoin
    cubsagg = pd.merge(left, right, how='left', left_on='teamID', right_on='tres', suffixes=('_x', '_y'))
    cubsagg.to_csv("csv/cubsagg.csv", index=False, encoding="utf-8")
    # Cubs players
    xreport.loc[20, 'status'] = 'OK'
    print("Cubs aggregate done")




    # start cubs batting stats
    left = CHCroster
    right = BSselect
    cubsBShit = pd.merge(left, right, how='left', left_on='posName', right_on='Name', suffixes=('_x', '_y'))
    cubsBShit = cubsBShit[cubsBShit.Name.notnull()]
    cubsBShit.loc[:, 'posnum'] = cubsBShit['posnum'].astype(int).astype(str)
    cubsBShit.loc[:, 'PA'] = cubsBShit['PA'].astype(int)
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
    # Cubs batting
    xreport.loc[21, 'status'] = 'OK'
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
    # Cubs pitching
    xreport.loc[22, 'status'] = 'OK'
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

    mpl.rcParams['xtick.labelsize'] = 17
    mpl.rcParams['ytick.labelsize'] = 17
    mpl.rcParams['lines.linewidth'] = 2

    #mpl.rcParams['font.sans-serif'].insert(0, 'Helvetica')

    #sns.set(font="Helvetica")

    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['font.size'] = 11
    mpl.rcParams['text.usetex'] = False
    mpl.rcParams['svg.fonttype'] = 'none'

    my_dpi=150

    #mpl.rcParams['pdf.fonttype'] = 42 # allows SVG text to be saved as editable

    plt.style.use(['ggplot'])

    from scipy.stats import norm

    # Plotting
    xreport.loc[23, 'status'] = 'OK'
    print('plotting ready')

    # ERA vs Batting average
    plt.figure()
    g = sns.regplot(data=result3, x='AVGbat', y='ERA',
                    fit_reg=True,
                    scatter_kws={'facecolors':result3['color'],"alpha":0.8,"s":70,'edgecolor':'none'},
                    line_kws={"color":"orange","lw":1}
                   )
    g.figure.set_size_inches(8,8)
    plt.ylabel('ERA', fontsize=16, fontweight='bold')
    plt.xlabel('BATTING AVERAGE', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/BAvERA.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # WAR stats
    plt.figure()
    g = sns.regplot(data=result3, x='WARbat', y='WARpitch',
                    fit_reg=True,
                    scatter_kws={'facecolors':result3['color'],"alpha":0.8,"s":70,'edgecolor':'none'},
                    line_kws={"color":"orange","lw":1}
                   )
    g.figure.set_size_inches(8,8)
    plt.ylabel('WAR PITCHING', fontsize=16, fontweight='bold')
    plt.xlabel('WAR BATTING', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/WAR.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # offense stats
    plt.figure()
    g = sns.regplot(data=result3, x='wOBA', y='RBI',
                    fit_reg=True,
                    scatter_kws={'facecolors':result3['color'],"alpha":0.8,"s":70,'edgecolor':'none'},
                    line_kws={"color":"orange","lw":1}
                   )

    g.figure.set_size_inches(8,8)
    plt.ylabel('RBI', fontsize=16, fontweight='bold')
    plt.xlabel('WEIGHTED ON-BASE AVG. (wOBA)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/offense.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # defense stats
    plt.figure()
    g = sns.regplot(data=result3, x='BABIP', y='FIP',
                    fit_reg=True,
                    scatter_kws={'facecolors':result3['color'],"alpha":0.8,"s":70,'edgecolor':'none'},
                    line_kws={"color":"orange","lw":1}
                   )
    g.figure.set_size_inches(8,8)
    plt.ylabel('FIELDING INDEPENDENT PITCHING (FIP)', fontsize=16, fontweight='bold')
    plt.xlabel('BA ON BALLS IN PLAY (BABIP)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/defense.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # bar plot, start with sorting
    # need to reset the index
    dfHR = result3.sort_values(by='HR', ascending=False).reset_index(drop=True)
    dfHR.to_csv("csv/dfHR.csv", index=False, encoding="utf-8")
    # clear the plt figure
    plt.figure()
    plt.xlim(0, 350)
    g = sns.barplot(
        x='HR',
        y='Team',
        data=dfHR,
        palette=dfHR['color']
    )
    plt.plot([307, 307], [-10, 30], color="#FF9C00", linewidth=2)
    g.figure.set_size_inches(8,14)
    g.set_ylabel('TEAM', fontsize=16, fontweight='bold')
    g.set_xlabel('HOME RUNS', fontsize=16, fontweight='bold')
    # placing the bar labels
    for p in g.patches:
        width = math.ceil( p.get_width() )
        g.text(width*1.04, p.get_y() + p.get_height()/1.25,
                "{:" ">6}".format( width ),
                fontsize=15, color="black", fontweight='bold', zorder=10)
    g.figure.savefig('static/img/HR.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()
    # League plots
    xreport.loc[24, 'status'] = 'OK'
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
            df.loc[0, 'hitperc'] = np.round( (row.BB / row.PA)*100,1 )
            df.loc[1, 'hitperc'] = np.round( (row.SO / row.PA)*100,1 )
            df.loc[2, 'hitperc'] = np.round( (row.H / row.PA)*100,1 )
            onebs = row.H - ( row.dbls + row.trps + row.HR )
            df.loc[3, 'hitperc'] = np.round( (onebs / row.H)*100,1 )
            df.loc[4, 'hitperc'] = np.round( (row.dbls / row.H)*100,1 )
            df.loc[5, 'hitperc'] = np.round( (row.trps / row.H)*100,1 )
            df.loc[6, 'hitperc'] = np.round( (row.HR / row.H)*100,1 )
        # start the plot
        plt.figure()
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
        style = dict(fontsize=18, color='black')
        #style = dict(fontsize=18, family='Helvetica-Bold', color='black')
        plt.text(0, 89, "As % of PA", **style)
        plt.text(3, 89, "As % of hits", **style)
        g.set_ylabel('% Of PLATE APPEARANCES | HITS', fontsize=16, fontweight='bold')
        g.set_xlabel('PLATE APPEARANCE RESULTS | HIT TYPE', fontsize=16, fontweight='bold')
        g.figure.savefig('static/img/sox' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight',dpi=my_dpi)
        plt.close()
    # Sox hitting charts
    xreport.loc[25, 'status'] = 'OK'
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
            df.loc[0, 'perc'] = row.FAperc
            df.loc[1, 'perc'] = row.FTperc
            df.loc[2, 'perc'] = row.FCperc
            df.loc[3, 'perc'] = row.FSperc
            df.loc[4, 'perc'] = row.FOperc
            df.loc[5, 'perc'] = row.SIperc
            df.loc[6, 'perc'] = row.SLperc
            df.loc[7, 'perc'] = row.CUperc
            df.loc[8, 'perc'] = row.EPperc
            df.loc[9, 'perc'] = row.CHperc
            df.loc[10, 'perc'] = row.SCperc
            df.loc[11, 'perc'] = row.KNperc
            df.loc[12, 'perc'] = row.KCperc
            df.loc[13, 'perc'] = row.UNperc

        df = df.fillna(value=0)
        # start the plot
        plt.figure()
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
        g.figure.savefig('static/img/soxpitch' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight',dpi=my_dpi)
        plt.close()
    # Sox pitching charts
    xreport.loc[26, 'status'] = 'OK'
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
            df.loc[0, 'hitperc'] = np.round( (row.BB / row.PA)*100,1 )
            df.loc[1, 'hitperc'] = np.round( (row.SO / row.PA)*100,1 )
            df.loc[2, 'hitperc'] = np.round( (row.H / row.PA)*100,1 )
            onebs = row.H - ( row.dbls + row.trps + row.HR )
            df.loc[3, 'hitperc'] = np.round( (onebs / row.H)*100,1 )
            df.loc[4, 'hitperc'] = np.round( (row.dbls / row.H)*100,1 )
            df.loc[5, 'hitperc'] = np.round( (row.trps / row.H)*100,1 )
            df.loc[6, 'hitperc'] = np.round( (row.HR / row.H)*100,1 )
        # start the plot
        plt.figure()
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
        style = dict(fontsize=18, color='black')
        #style = dict(fontsize=18, family='Helvetica-Bold', color='black')
        plt.text(0, 89, "As % of PA", **style)
        plt.text(3, 89, "As % of hits", **style)
        g.set_ylabel('% Of PLATE APPEARANCES | HITS', fontsize=16, fontweight='bold')
        g.set_xlabel('PLATE APPEARANCE RESULTS | HIT TYPE', fontsize=16, fontweight='bold')
        g.figure.savefig('static/img/cubs' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight',dpi=my_dpi)
        plt.close()
    # Cubs hitting charts
    xreport.loc[27, 'status'] = 'OK'
    print('cubs hitting charts done')


    # begin Cubs hitting charts

    for index, row in cubsPSpitch.iterrows():
        d = {'pitches': ['FASTBALL','FS-2SEAM','CUTTER','SPLIT-FINGER','FORKBALL', 'SINKER', 'SLIDER', 'CURVEBALL','EPHESUS','CHANGE-UP','SCREWBALL','KNUCKLEBALL','KNUCKLE-CURVE','UNKNOWN']}
        df = pd.DataFrame(data=d)
        df['perc'] = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        if ( row.Pitches == 0):
            junkvar = []
        else:
            df.loc[0, 'perc'] = row.FAperc
            df.loc[1, 'perc'] = row.FTperc
            df.loc[2, 'perc'] = row.FCperc
            df.loc[3, 'perc'] = row.FSperc
            df.loc[4, 'perc'] = row.FOperc
            df.loc[5, 'perc'] = row.SIperc
            df.loc[6, 'perc'] = row.SLperc
            df.loc[7, 'perc'] = row.CUperc
            df.loc[8, 'perc'] = row.EPperc
            df.loc[9, 'perc'] = row.CHperc
            df.loc[10, 'perc'] = row.SCperc
            df.loc[11, 'perc'] = row.KNperc
            df.loc[12, 'perc'] = row.KCperc
            df.loc[13, 'perc'] = row.UNperc

        df = df.fillna(value=0)
        # start the plot
        plt.figure()
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
        g.figure.savefig('static/img/cubspitch' + str( row.lastname ) + str( row.posnum ) + '.png',bbox_inches='tight',dpi=my_dpi)
        plt.close()
    # Cubs pitching charts
    xreport.loc[28, 'status'] = 'OK'
    print('Cubs pitching charts done')


    # -------------------------------
    # Now the head 2 head charts

    #set violin plot pallete
    my_pal = {"WHITE SOX": "#000000", "CUBS": "#000FFF"}

    # Collect the batting stats, minus pitchers

    h2hhitting = soxBShit
    h2hhitting['setcol'] = '#000000'
    h2hhitting['Team'] = 'WHITE SOX'
    h2hcubshit = cubsBShit
    h2hcubshit['setcol'] = '#000FFF'
    h2hcubshit['Team'] = 'CUBS'
    h2hhitting = h2hhitting.append(h2hcubshit)
    ispitcher = ['P']
    h2hhit = h2hhitting[~h2hhitting.position.isin(ispitcher)]
    # h2h batting stats
    xreport.loc[29, 'status'] = 'OK'
    print('batting stats appended')

    # Batting avg h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="AVG", data=h2hhit, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="AVG", data=h2hhit,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="AVG", data=h2hhit, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('BATTING AVERAGE', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hAVG.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # wOBA avg h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="wOBA", data=h2hhit, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="wOBA", data=h2hhit,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="wOBA", data=h2hhit, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('WEIGHTED ON-BASE AVG. (wOBA)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hwOBA.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # wRAA avg h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="wRAA", data=h2hhit, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="wRAA", data=h2hhit,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="wRAA", data=h2hhit, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('WEIGHTED RUNS ABOVE AVG. (wRAA)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hwRAA.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # RAR avg h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="RAR", data=h2hhit, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="RAR", data=h2hhit,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="RAR", data=h2hhit, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('RUNS ABOVE REPLACEMENT (RAR)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hRARhit.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # FLD avg h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="Fld", data=h2hhit, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="Fld", data=h2hhit,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="Fld", data=h2hhit, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('FIELDING RUNS ABOVE AVG. (Fld)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hFld.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # WAR hitting h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="WAR", data=h2hhit, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="WAR", data=h2hhit,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="WAR", data=h2hhit, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('WINS ABOVE REPLACEMENT (WAR)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hWARhit.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # h2h batting charts
    xreport.loc[30, 'status'] = 'OK'
    print('h2h batting done')

    # Collect the pitching stats
    h2hpitching = soxPSpitch
    h2hpitching['setcol'] = '#000000'
    h2hpitching['Team'] = 'WHITE SOX'
    h2hcubs = cubsPSpitch
    h2hcubs['setcol'] = '#000FFF'
    h2hcubs['Team'] = 'CUBS'
    h2hpitching = h2hpitching.append(h2hcubs)
    # h2h pitching stats
    xreport.loc[31, 'status'] = 'OK'
    print('pitching stats appended')

    # ERA h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="ERA", data=h2hpitching, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="ERA", data=h2hpitching,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="ERA", data=h2hpitching, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('EARNED RUN AVERAGE', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hERA.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # FIP h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="FIP", data=h2hpitching, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="FIP", data=h2hpitching,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="FIP", data=h2hpitching, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('FIELDING INDEPENDENT PITCHING (FIP)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hFIP.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # WHIP h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="WHIP", data=h2hpitching, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="WHIP", data=h2hpitching,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="WHIP", data=h2hpitching, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('WALKS, HITS PER INNING (WHIP)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hWHIP.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()


    # BABIP h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="BABIP", data=h2hpitching, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="BABIP", data=h2hpitching,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="BABIP", data=h2hpitching, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('BA ON BALLS IN PLAY (BABIP)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hBABIP.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # WPA h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="WPA", data=h2hpitching, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="WPA", data=h2hpitching,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="WPA", data=h2hpitching, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    # Add labels to the plot
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('WIN PROBABILTY ADDED (WPA)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hWPA.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()


    # RAR h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="RAR", data=h2hpitching, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="RAR", data=h2hpitching,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="RAR", data=h2hpitching, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    # Add labels to the plot
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('RUNS ABOVE REPLACEMENT (RAR)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hRAR.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # WAR h2h plot
    plt.figure()
    gs = sns.violinplot(x="Team", y="WAR", data=h2hpitching, inner=None, linewidth=0, palette=my_pal)
    plt.setp(gs.collections, alpha=.5)
    g = sns.boxplot(x="Team", y="WAR", data=h2hpitching,
                    showcaps=True,
                    boxprops={'facecolor':'None', 'edgecolor': '#8FBC8B', 'zorder': 1 },
                    whiskerprops={'color': '#8FBC8B'},
                    capprops={'color': '#8FBC8B'},
                    medianprops={'color': '#8FBC8B'},
                    showfliers=False)
    g = sns.swarmplot(x="Team", y="WAR", data=h2hpitching, color="orange")
    g.figure.set_size_inches(6,6)
    g.grid(axis='y', linewidth=2)
    tick_locator = ticker.MaxNLocator(10)
    g.yaxis.set_major_locator(tick_locator)
    # Add labels to the plot
    g.set_xlabel('', fontsize=2)
    g.set_ylabel('WINS ABOVE REPLACEMENT (WAR)', fontsize=16, fontweight='bold')
    g.figure.savefig('static/img/h2hWAR.png',bbox_inches='tight',dpi=my_dpi)
    plt.close()

    # h2h pitching charts
    xreport.loc[32, 'status'] = 'OK'
    print('h2h pitching done')


    # -------------------------------
    # Freeze the app

    from flask_frozen import Freezer
    from app import app, get_csv
    freezer = Freezer(app)

    if __name__ == '__main__':
        app.config.update(FREEZER_RELATIVE_URLS=True)
        freezer.freeze()

    # site frozen
    xreport.loc[33, 'status'] = 'OK'
    print('Frozen')

    # Now rename the build directory

    shutil.move('build', 'docs')

    print('docs folder done')

    # pushed to web
    xreport.loc[34, 'status'] = 'OK'

except Exception as e:
    xreport.to_csv("csv/xreport.csv", index=False, encoding="utf-8")

print('all done')
