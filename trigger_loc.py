#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 13:54:04 2026

@author: gregory
"""

import sys
sys.path.append('/home/gregory/Documents/mermaid_glap')

import obspy
from obspy.core import UTCDateTime
from obspy import read
from datetime import datetime
import matplotlib.pyplot as plt
from my_code.mer_data_invst_f import mermaid_df,reciever_loc_all, plot_save_spec

'''
This code is intended as a command line/console function

Allows plotting of mermaid trigger location current data path is set for Galapagos but Indian ocean & Med will work if set 

Steps 
- Takes a start and end date converting it intodash date (not nessisary if i change Mer_df )
- Converts every sac datafile of GLAP into a data frame using mermaid_df 
- Gives option to save spectograms for all data into temp using plot_sace_spec
- Then plots onto a map of bathymoyry around Galap using reciever_loc_all

Things to NOTE
- As plots inidicual dates in legend not suited for many dates only a month or so, It will do it just not be as clear 

'''

default_start = '20150901'
default_end = '20151001'
startdate = input(f'Enter a date for start of timeframe in YYYYMMDD default is [{default_start}] : ') or default_start # the or is defults
startdate = datetime.strptime(startdate, "%Y%m%d").strftime("%Y-%m-%d")

enddate = input(f'Enter end date default [{default_end}]: ') or default_end
enddate = datetime.strptime(enddate, "%Y%m%d").strftime("%Y-%m-%d")


    
# Reading in both identified and non also speed up using this slighly
st = read('data/galapagos/mermaid*/*identified/sac/m*.sac')

mer_df = mermaid_df(st)

spec = input ('Want spectograms of events (save to /temp)? y/n : ') or 'n'

if spec == 'y':
    plot_save_spec(st,startdate,enddate)
    

mer_df['date'] = mer_df['starttime'].apply(lambda x: x.date())

# Checking correct dates error 
date_min = mer_df['starttime'].min()
date_max = mer_df['starttime'].max()

if UTCDateTime(startdate) < date_min or UTCDateTime(enddate) > date_max:
    raise ValueError(f"Error: requested timeframe ({startdate} to {enddate}) is outside "
          f"the available data range ({date_min.date:. f10} to {date_max.date:. f10}).")


title= f'Mermaid record triggers location from {startdate} to {enddate}'

#title commented incase i actually want to name it 
#title='Unidentified mermaid record with rythmic rumbling 2015-01-20 to 2015-01-25'

input_mer_df = mer_df[
    (mer_df['starttime'] >= startdate) &
    (mer_df['starttime'] < enddate)
]

fig = reciever_loc_all(input_mer_df, title=title)

fig.savefig('test.png', dpi=1000)
plt.show()