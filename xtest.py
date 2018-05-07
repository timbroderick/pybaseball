import pandas as pd

import warnings
warnings.filterwarnings("ignore")


data = {'task': ['task0','task1','task2','task3']}
xreport = pd.DataFrame(data=data)
xreport ['status'] = ['Problem','Problem','Problem','Problem']

xreport.loc[0, 'status'] = 'OK'
xreport.loc[1, 'status'] = 'OK'
xreport.loc[2, 'status'] = 'OK'
xreport.loc[3, 'status'] = 'OK'

xreport.to_csv("csv/xreport.csv", index=False, encoding="utf-8")
