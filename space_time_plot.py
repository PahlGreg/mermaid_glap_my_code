#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 09:54:46 2026

@author: gregory
"""

# first need to read in and add a header
from obspy.core import UTCDateTime
from obspy import Stream
from obspy import read
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import my_code.mer_plot_f as m 
import matplotlib.dates as mdates

'''
What this code does

Using classification (spectrograms in a file with set FILE name )
Obtains traces using names of spectograms 
Assines a Kuser0 label then plots timeline according to that label

Also a simple code that plots the entire dataset#

OUTPUTS 
A matplotlib timeline with symbols for type 

'''
# %%Type
#Glitches plot -------------------------------------------------------------------
title_template = 'Timeline of glitch & low frequency signals in uncatagorised triggers recorded by mermaid in Galapagos Deployment, Total:{n} types contained'
CLASSIFICATIONS = [
    # (folder_name,   kuser0 code, print label)
    ('Contains_pure','P', 'Pure Glitches'),
    ('Contains_low','Q', 'Low freq triggers'),
    ('Contains_hills','R','lower frequency glitches'),
    ('Contains_onoff','S','Period of almost 0 counts')
]
header_vals=['P','Q','R','S']
marker_map= ["o", "^", "s", "D"]
colours=['aqua','blue','teal','mediumspringgreen']

# General type ----------------------------------------------------
# title_template = 'Timeline of types of uncatagorised triggers recorded by mermaid in Galapagos Deployment, Total:{length} Triggers'
# CLASSIFICATIONS = [
#     # (folder_name,   kuser0 code, print label)
#     ('Contains_glitch', 'A', 'Gliches & unidentified triggers'),
#     ('Contains_Twave',  'B', 'T waves'),
#     ('Contains_local',  'C', 'Event')
# ]
# marker_map= ['o','+','x']
# header_vals=['A','B','C']
# colours = ['blue','firebrick','darkviolet']


# %%



# First importing all and adding user2 header (which is type)
# st = read('data/altered_glap/m20.20160301T*.sac')
st = read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')

for tr in st:
    tr.stats.sac.kuser0 = ''
    t = UTCDateTime(tr.stats.starttime)
    starttime = str(t.strftime("%Y%m%dT%H%M%S"))
    tr.write(f'data/altered_glap/m{str(tr.stats.station)}.{starttime}.sac', format='SAC')

def read_unidentified_type(type_path):
    '''
    Reads in a sac file according to the names of spectrograms for labellign perposes
    this has been changed to the new path
    '''
    files = [f.name for f in Path(type_path).iterdir() if f.is_file()]  # just filenames, files only
    filenames = [f[:-4] if f.endswith('.png') else f for f in files]
    
    st = Stream() 
    for name in filenames:
        filepath = Path(f'data/altered_glap/{name}.sac')
        if filepath.exists():
            st += read(filepath)
        else:
            continue
    return st       

def write_traces (st):
    for tr in st:
        t = UTCDateTime(tr.stats.starttime)
        starttime = str(t.strftime("%Y%m%dT%H%M%S"))
        tr.write(f'data/altered_glap/m{str(tr.stats.station)}.{starttime}.sac', format='SAC')

def tag_and_write(st, code, label):
    """Append a classification code to kuser0 for every trace, write, and report count."""
    for tr in st:
        tr.stats.sac.kuser0 = (tr.stats.sac.kuser0 or '') + code
    print(label, len(st))
    write_traces(st)
    n = len(st)
    return n
#------------- Define type of data above -----------------------

BASE_PATH = Path('/home/gregory/Documents/mermaid_glap/random_data')
#Picks up from folder with name, writes the kuser0 code then prints label of what that code means 
n=0
for folder_name, code, label in CLASSIFICATIONS:
    path = BASE_PATH / folder_name
    st = read_unidentified_type(path)
    n = n + tag_and_write(st, code, label)
# --- Final pass: tag everything currently in altered_glap as 'entire' ---
st = read('data/altered_glap/m*.sac')
tag_and_write(st, 'Z', 'entire')
# %% plotting timeline First getting data time in pandas df

st = read('data/altered_glap/m*.sac')

def mermaid_df(st):
    mer_record=[]                
    for tr in st:
        mer_record.append({
            "network": tr.stats.network,
            "station": int(tr.stats.station),
            "starttime": tr.stats.starttime.datetime,
            "endtime": tr.stats.endtime,
            "sampling_rate": tr.stats.sampling_rate,
            "delta": tr.stats.delta,
            "npts": tr.stats.npts,
            "calib":tr.stats.calib,
            "stla": tr.stats.sac.get("stla"),
            "stlo": tr.stats.sac.get("stlo"),
            "stdp": tr.stats.sac.get("stdp"),
            'SNR (USER0)': tr.stats.sac.get('user0'),
            'CRITERION (USER1)': tr.stats.sac.get('user1'),
            'Types': tr.stats.sac.get('kuser0')
        })

    mer_df = pd.DataFrame(mer_record)
    
    return mer_df

# Reads into df then adds a column for timestamp
mer_df = mermaid_df(st)
timestamps_list=[]
for tr in st:
    time= tr.stats.starttime.datetime # Bare in min the starttime is not trigger time and the time between varies
    timestamps_list.append(time)
mer_df['timestamps'] = timestamps_list

#need to subtract first record timestamp
st_ent = read('data/galapagos/mermaid*/*identified/sac/m*.*.sac')
mer_df_ent = mermaid_df(st_ent)

stations=mer_df['station'].unique()
# Finds the station first recording to use as start
date_min=[]
date_max=[]
for station in stations:
    date_min.append(
        (mer_df_ent.loc[mer_df_ent['station']==station,'starttime'].min())
        )
    date_max.append(
        (mer_df_ent.loc[mer_df_ent['station']==station,'starttime'].max())
        )

# %% Plotting timelien for each station



n_stations=len(stations)
fig,axs = plt.subplots(n_stations,1,figsize=(15,0.5*n_stations),sharex=True,
                       gridspec_kw={'hspace': 0})
axs=axs.flatten()

############### IMPORTANT THIS IS WHATS ACTUALLY PLOTTED
header_names=[name[2] for name in CLASSIFICATIONS]

for i,station in enumerate(stations):
    ax = axs[i]
    times_df = mer_df.loc[mer_df['station'] == station]
    times = times_df['timestamps']

    for j, (header_val, marker) in enumerate(zip(header_vals, marker_map)):
       subset = times_df[times_df['Types'].str.contains(header_val, na=False)]
       ax.scatter(subset['timestamps'], [0] * len(subset), marker=marker, label=header_names[j],color=colours[j])
    
    ax.axvspan(date_min[i], date_max[i], color='red', alpha=0.15,label='Mermaid first to last trigger')
    ax.set_title(f'm{station}', loc="left", fontsize=10, fontweight="bold",y=0)
    
    ax.get_yaxis().set_visible(False)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

#     ax.xaxis.set_major_locator(mdates.MonthLocator())
#     ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

# fig.autofmt_xdate()
# plt.tight_layout()
handles, labels = axs[0].get_legend_handles_labels()
axs[0].legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                      ncols=5, borderaxespad=0.)
title = title_template.format(n=n,length=len(st))
fig.suptitle(title, fontsize=12)
plt.show()


# %% Plotting just identified

st = read('data/galapagos/mermaid*/identified/sac/m*.*.sac')

mer_df=mermaid_df(st)
# Reads into df then adds a column for timestamp
mer_df = mermaid_df(st)
timestamps_list=[]
for tr in st:
    time= tr.stats.starttime.datetime # Bare in min the starttime is not trigger time and the time between varies
    timestamps_list.append(time)

mer_df['timestamps'] = timestamps_list

#Unidentified
unst = read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')
# Reads into df then adds a column for timestamp
unmer_df = mermaid_df(unst)
untimestamps_list=[]
for tr in unst:
    time= tr.stats.starttime.datetime # Bare in min the starttime is not trigger time and the time between varies
    untimestamps_list.append(time)

unmer_df['timestamps'] = untimestamps_list

n_stations=len(stations)
fig,axs = plt.subplots(n_stations,1,figsize=(20,0.5*n_stations),sharex=True,
                       gridspec_kw={'hspace': 0})
axs=axs.flatten()

for i,station in enumerate(stations):
    ax = axs[i]
    times_df = mer_df.loc[mer_df['station'] == station]
    ax.scatter(times_df['timestamps'], [0] * len(times_df),label='Triggers with identified events',color='blue')
    
    untimes_df = unmer_df.loc[unmer_df['station'] == station]
    ax.scatter(untimes_df['timestamps'], [0] * len(untimes_df),label='Unidentified Triggers',color='red', marker='s',s=4)

    ax.axvspan(date_min[i], date_max[i], color='red', alpha=0.15,label='Mermaid first to last trigger')
    ax.set_title(f'm{station}', loc="left", fontsize=10, fontweight="bold",y=0)
    
    ax.get_yaxis().set_visible(False)
    ax.grid(axis='x', linestyle='--', alpha=0.5)

#     ax.xaxis.set_major_locator(mdates.MonthLocator())
#     ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

# fig.autofmt_xdate()
# plt.tight_layout()
handles, labels = axs[0].get_legend_handles_labels()
axs[0].legend(handles, labels, bbox_to_anchor=(0., 1.02, 1., .102), loc='lower right',
                      ncols=4, borderaxespad=0.)
fig.suptitle(f'Timeline of catagorised event triggers recorded by mermaid in Galapagos Deployment, Total:{len(st)+len(unst)} Triggers', fontsize=12)
plt.show()
