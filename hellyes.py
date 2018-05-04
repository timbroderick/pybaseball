import os
import shutil

import warnings
warnings.filterwarnings("ignore")

# ---------
# first remove the old directories
shutil.rmtree('/Users/jeff/Desktop/conda/anaconda/envs/notebook/1work/pybaseball/testing directory', ignore_errors=True)

os.mkdir('/Users/jeff/Desktop/conda/anaconda/envs/notebook/1work/pybaseball/new testing directory')
