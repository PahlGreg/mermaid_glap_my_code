#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 15:59:11 2026

@author: gregory
"""

import sys
import os
import glob
sys.path.append('/home/gregory/Documents/mermaid_glap')

from obspy import read

from datetime import datetime
from my_code.mer_data_invst_f import plot_save_spec




# %%


# Clear temp folder
folder = '/home/gregory/Documents/mermaid_glap/Plots/spectrograms/temp'
for file in glob.glob(os.path.join(folder, "*")):
    if os.path.isfile(file):
        os.remove(file)


print('Options for selecting and plotting multiple mermaid spectograms within a time frame')

# Need to sort out stations option not important now
# stations=(input('Which stations are wanted? Glap has [10,19,20,21,22,23,24,25,26] star for all'
#                    ': ')) or '*'
stations = '*'
print('Ensure within Glap data timeframe (2014-05-11 to 2016-10-15) remember deployment dates differ, see documentation')
startdate = input('Enter a date for start of timeframe in YYYYMMDD: ') or '20150323' # the or is defults
startdate = datetime.strptime(startdate, "%Y%m%d").strftime("%Y-%m-%d")

enddate = input('Enter end date: ') or '20150324'
enddate = datetime.strptime(enddate, "%Y%m%d").strftime("%Y-%m-%d")

station = input('An individual station or *?') or '*'

while True:
    if_id = input('Which type of event, identified, unidentified or both (i/un/*)? ') or '*'
    if if_id == 'i':
        if_id = 'i'
        break
    elif if_id == 'un':
        if_id = 'uni'
        break
    elif if_id == '*':
        if_id = '*i'
        break
    else:
        print('Invalid choice')

    
datafile = f'data/galapagos/mermaid*/{if_id}dentified/sac/m{station}.*.sac'

st= read(datafile)


plot_save_spec(st,startdate,enddate)
