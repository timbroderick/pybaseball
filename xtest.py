import pandas as pd

import warnings
warnings.filterwarnings("ignore")


taskdata = {'task': ['Packages loaded','old directories removed','standings','team batting','team pitching','Sox sched','Cubs sched','batting stats','pitching stats','Sox roster','Cubs roster','stadings appended','standings joined','batting stats joined','pitching stats joined','Sox games','Sox players','Sox batting','Sox pitching','Cubs games','Cubs players','Cubs batting','Cubs pitching','Plotting','League plots','Sox hitting charts','Sox pitching charts','Cubs hitting charts','Cubs pitching charts','h2h batting stats','h2h batting charts','h2h pitching stats','h2h pitching charts','site frozen','pushed to web']}
xreport = pd.DataFrame(data=taskdata)
xreport ['status'] = ['Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem','Problem']

try:
	# packages
	xreport.loc[0, 'status'] = 'OK'

	# old directories removed
	xreport.loc[1, 'status'] = 'OK'

	# standings
	xreport.loc[2, 'status'] = 'OK'

	# team batting
	xreport.loc[3, 'status'] = 'OK'

	# team pitching
	xreport.loc[4, 'status'] = 'OK'

	# Sox sched
	xreport.loc[5, 'status'] = 'OK'

	# Cubs sched
	xreport.loc[6, 'status'] = 'OK'

	# batting stats
	xreport.loc[7, 'status'] = 'OK'

	# pitching stats
	xreport.loc[8, 'status'] = 'OK'

	# Sox roster
	xreport.loc[9, 'status'] = 'OK'

	# Cubs roster
	xreport.loc[10, 'status'] = 'OK'

	# stadings appended
	xreport.loc[11, 'status'] = 'OK'

	# standings joined
	xreport.loc[12, 'status'] = 'OK'

	# batting stats joined
	xreport.loc[13, 'status'] = 'OK'

	# pitching stats joined
	xreport.loc[14, 'status'] = 'OK'

	# Sox games
	xreport.loc[15, 'status'] = 'OK'

	# Sox players
	xreport.loc[16, 'status'] = 'OK'

	# Sox batting
	xreport.loc[17, 'status'] = 'OK'

	# Sox pitching
	xreport.loc[18, 'status'] = 'OK'

	# Cubs games
	xreport.loc[19, 'status'] = 'OK'

	# Cubs players
	xreport.loc[20, 'status'] = 'OK'

	# Cubs batting
	xreport.loc[21, 'status'] = 'OK'

	# Cubs pitching
	xreport.loc[22, 'status'] = 'OK'

	# Plotting
	xreport.loc[23, 'status'] = 'OK'

	# League plots
	xreport.loc[24, 'status'] = 'OK'

	# Sox hitting charts
	xreport.loc[25, 'status'] = 'OK'

	# Sox pitching charts
	xreport.loc[26, 'status'] = 'OK'

	# Cubs hitting charts
	xreport.loc[27, 'status'] = 'OK'

	# Cubs pitching charts
	xreport.loc[28, 'status'] = 'OK'

	# h2h batting stats
	xreport.loc[29, 'status'] = 'OK'

	# h2h batting charts
	xreport.loc[30, 'status'] = 'OK'

	# h2h pitching stats
	xreport.loc[31, 'status'] = 'OK'

	# h2h pitching charts
	xreport.loc[32, 'status'] = 'OK'

	# site frozen
	xreport.loc[33, 'status'] = 'OK'

	# pushed to web
	xreport.loc[34, 'status'] = 'OK'

except Exception as e:
	xreport.to_csv("csv/xreport.csv", index=False, encoding="utf-8")



