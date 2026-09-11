#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  4 12:25:36 2026

@author: gregory

Aims to analyse the unidentified record 
-------------------------------------
- Code Reads the unidentified record in as a DF, then plots amount of days with >2 readings
- reciever_loc_unid: Function plots the location of unidentified readings 
    Has some code bellow to select certain days to plot to analyse multireading days

- Code uses multiplot_filt, basic_proc from plot_mer to produce raw and 
    filtered seimogram sof the unidentified record
"""

from obspy.geodetics import FlinnEngdahl
import obspy.signal
import obspy
from obspy.core import UTCDateTime
from obspy import read, Stream
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path
import my_code.mer_plot_f as m 
from my_code.mer_plot_f import spectrogram_plot_uni
from my_code.mer_data_invst_f import data_plots_un_type 


# %%



# Making the df of unidentified mermaids

'''
Reading the unidentified mer

THen counting the amount of records per day
'''
st = read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')



unmer_df = m.mermaid_df(st)

# for tr in st:
#     unmer_record.append({
#         "network": tr.stats.network,
#         "station": int(tr.stats.station),
#         "starttime": tr.stats.starttime.datetime,
#         "endtime": tr.stats.endtime,
#         "sampling_rate": tr.stats.sampling_rate,
#         "delta": tr.stats.delta,
#         "npts": tr.stats.npts,
#         "calib":tr.stats.calib,
#         "stla": tr.stats.sac.get("stla"),
#         "stlo": tr.stats.sac.get("stlo"),
#         "stdp": tr.stats.sac.get("stdp"),
#         "dist": tr.stats.sac.get("dist"),
#         "evla": tr.stats.sac.get("evla"),
#         "evlo": tr.stats.sac.get("evlo"),
#         "gcarc": tr.stats.sac.get("gcarc"),
#         "evdp": tr.stats.sac.get("evdp"),
#         'SNR (USER0)': tr.stats.sac.get('user0'),
#         'CRITERION (USER1)': tr.stats.sac.get('user1')
#     })

# unmer_df = pd.DataFrame(unmer_record)

unmer_df['date'] = unmer_df['starttime'].apply(lambda x: x.date())
trig_date = unmer_df.groupby(['station','date']).size()


results = []

stations = unmer_df['station'].unique()

for sensor in stations:
    #makes a seperate data fram that just has the counts 
    counts = (
        unmer_df#[unmer_df['station'] == sensor]
        .groupby('date')
        .size()
    )
    #Makes a list of the counts as a dictionary
    for date, count in counts.items():
        if count > 2:
            results.append({
                'station': sensor,
                'date': date,
                'count': count
            })

results_df = pd.DataFrame(results)

#Prints the amount of unique identifiecations per day
print(results_df.to_string(index=False))

# %% Plot of unidentified can be used to locate where station saw event 
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

from my_code.mer_data_invst_f import reciever_loc_unid
title='Unidentified mermaid record with rythmic rumbling 2015-01-20 to 2015-01-25'
unmer_n = unmer_df[unmer_df['station'].isin([19,21,22])] #needc to select the stations within that timefram maybe change
int_unmer_n = unmer_n[
    (unmer_n['starttime'] >= '2015-01-20') &
    (unmer_n['starttime'] < '2015-01-25')
]
reciever_loc_unid(int_unmer_n, title=title)

# %% Plotting seismogram for unfiltered
from my_code.mer_plot_f import multiplot_filt, basic_proc


'''
One of th best wats to filter is the SNR 

'''
stations = unmer_df['station'].unique()

# st = read('data/galapagos/mermaid*/unidentified/sac/m22.20160811*.sac')

# for sensor in stations[0:5]:
st = read(f'data/galapagos/mermaid*/unidentified/sac/m*.20150323*.sac')

st1_filt = st.copy()

basic_proc(st1_filt)
freq_maximum = 5
freq_minimum =0.7
#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'
st1_filt = st1_filt.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

multiplot_filt(st,st1_filt,filt_type='bandpass', freq_max = freq_maximum, freq_min = freq_minimum)
plt.show()

# %% getting amount of mermaid that seen same events

unmer_df['date'] = unmer_df['starttime'].apply(lambda x: x.date())
trig_date = unmer_df.groupby(['station','date']).size()


results = []

stations = unmer_df['station'].unique()

unmer_df['timestamp'] = unmer_df['starttime'].apply(
    lambda x: UTCDateTime(x).timestamp
)
# Sort by timestamp
unmer_df = unmer_df.sort_values('timestamp').reset_index(drop=True)

#Finds if the time difference is within 20 minutes and on a different station
mask = (
    (
        (unmer_df['timestamp'].diff() <= (60*20)) &
        (unmer_df['station'] != unmer_df['station'].shift())
    )
    |
    (
        (unmer_df['timestamp'].diff(-1).abs() <= (60*20)) &
        (unmer_df['station'] != unmer_df['station'].shift(-1))
    )
)

within_min = unmer_df[mask]


# Create a new group whenever the gap exceeds 1 hour
within_min['group'] = (
    within_min['timestamp'].diff().fillna(np.inf) > 3600
    ).cumsum()

counts = within_min.groupby('group').size()

#Obtatining stations of each
stations_per_group = (
    within_min.groupby('group')['station']
    .unique()
    .reset_index(name='stations')
    )


for group, count in counts.items():
    if count > 2:
        group_df = within_min[within_min['group'] == group]
        
        results.append({
            'start_time': group_df['starttime'].min(),
            'end_time': group_df['starttime'].max(),
            'count': count,
            'stations': list(group_df['station'])
            })
        
        
        for x in range(min(group_df.index),max(group_df.index),1):
            start =(within_min['starttime'][x] - pd.Timedelta(seconds=0.01)).strftime("%Y%m%dT%H%M")
            station= group_df['station'][x]

            st = read(f'data/galapagos/mermaid*/unidentified/sac/m{station}.{start}*.sac')
            
            st.write(f'data/glap_pot_identify/m{station}.{start}.sac',format='SAC')
results_df = pd.DataFrame(results)

#Prints the amount of unique identifiecations per day
print(results_df.to_string(index=False))




# %% Single specro plot

st = read('data/galapagos/mermaid*/unidentified/sac/m21.20151130*.sac')

freq_maximum=5
freq_minimum=2
spec_freq_maximum = 5
spec_freq_minimum = 0.1
nfft = int(len(st[0].data)/20)

fig = spectrogram_plot_uni(
    st,freq_maximum, freq_minimum,
    spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
    nfft=nfft,log=True)
plt.show()
# %% Single multi bandpass
'''
This is the code that also pltos a map

'''

st = read('data/galapagos/mermaid*/unidentified/sac/m21.20151130*.sac')

freq_maximum=2
freq_minimum=0.5
spec_freq_maximum = 5
spec_freq_minimum = 0.1
freq_max2 = 10
freq_min2 = 2.5

nfft = int(len(st[0].data)/20)


fig = m.spectrogram_plot_uni(
    st[0:1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
    spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
    nfft=nfft,
    log=False,add_map=True,
    taper=('tukey',0.25)
    )
plt.show()

# %% Plotting spectrogram both log and non log


st = read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')

freq_maximum=5
freq_minimum=2
spec_freq_maximum = 5
spec_freq_minimum = 0.1

for i in range(len(st)):
    
    
    nfft = int(len(st[i].data)/20)
    
    
    fig = m.spectrogram_plot_uni(
        st[i:i+1],freq_maximum, freq_minimum,
        spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
        nfft=nfft,
        log=False,
        )
    plt.show()
    t= UTCDateTime(st[i].stats.starttime)
    time= t.strftime("%Y%m%dT%H%M%S")
    station=st[i].stats.station
    fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/UnGlap_spec/m{station}.{time}.png', dpi=300, bbox_inches='tight')
freq_maximum=5
freq_minimum=2
spec_freq_maximum = 5
spec_freq_minimum = 0.1
for i in range(len(st)):
    nfft = int(len(st[i].data)/20)
    
    
    fig = m.spectrogram_plot_uni(
        st[i:i+1],freq_maximum, freq_minimum,
        spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
        nfft=nfft,
        log=True,
        )
    plt.show()
    t= UTCDateTime(st[i].stats.starttime)
    time= t.strftime("%Y%m%dT%H%M%S")
    station=st[i].stats.station
    fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/UnGlap_spec/m{station}.{time}_log.png', dpi=300, bbox_inches='tight')
    
# %%
st=read('data/galapagos/mermaid*/*identified/sac/m*.20150525*.sac')
freq_maximum=2
freq_minimum=0.5
spec_freq_maximum = 5
spec_freq_minimum = 0.1
freq_max2 = 10
freq_min2 = 2.5

for i in range(len(st)):
        
    nfft = int(len(st[i].data)/20)

    fig = m.spectrogram_plot_uni(
        st[i:i+1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
        spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
        nfft=nfft,
        log=False,
        taper=('tukey',0.25)
        )
    
    plt.show()
    # t= UTCDateTime(st[i].stats.starttime)
    # time= t.strftime("%Y%m%dT%H%M%S")
    # station=st[i].stats.station
    # # Remember ti change save location
    # fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/spectrograms/search_for_rumblings/m{station}.{time}.png', dpi=200, bbox_inches='tight')
    
# %%
from my_code.mer_data_invst_f import mermaid_df

st = read('data/galapagos/mermaid*/identified/sac/m*.*.sac')

print(min(tr.stats.sac.stlo for tr in st))

#calculating months alive each
df = mermaid_df(st)
months=[]
for sensor in (df['station'].unique()):
    t1= df.loc[df['station']==sensor,['starttime']].min().item()
    t2= df.loc[df['station']==sensor,['starttime']].max().item()
    
    months.append((t2.year - t1.year) * 12 + (t2.month - t1.month))

st = read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')

mer_df = mermaid_df(st)
df = mer_df
# data_plots_un_amount(mer_df)
colours = [
    '#0072B2',  # blue
    '#E69F00',  # orange
    '#009E73',  # green
    '#D55E00',  # vermillion
    '#CC79A7',  # purple
    '#56B4E9',  # sky blue
    '#F0E442',  # yellow
    '#332288',  # black
    '#999999'   # grey
]

fig,ax = plt.subplots(1,1,figsize=(10,8))

  


stations_str=df['station'].astype(str).unique()
stations=df['station'].unique()
labels=[]

for i,s in enumerate(df['station'].unique()):
    labels.append(f'MERMAID {s}\nmonths alive ={months[i]}')

    
counts = df['station'].value_counts().sort_index()

bars = ax.bar(labels,counts,color=colours,edgecolor='k', linewidth=1)


#Months alive
t1= df['starttime'].min()
t2= df['starttime'].max()
months = (t2.year - t1.year) * 12 + (t2.month - t1.month)
events=df['starttime'].count()

ax.set_title(f'No trigger by mermaid uncatagorised: total={events} triggers | mission length = {months} months')

ax.set_xticklabels(labels, rotation=45, ha='right')
ax.set_ylabel('Number of triggers unidentified')   
# %% Stats of unidentified

st=read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')
entire_df = m.mermaid_df(st)
print('total unidentfied triggers:', len(st))

def read_unidenfied_type(type_path):
    files = [f.name for f in Path(type_path).iterdir() if f.is_file()]  # just filenames, files only
    filenames = [f[:-4] if f.endswith('.png') else f for f in files]
    
    st = Stream() 
    for name in filenames:
        filepath = Path(f'data/galapagos/mermaid{name[1:3]}/unidentified/sac/{name}.sac')
        if filepath.exists():
            st += read(str(filepath))
        else:
            continue
    return st        
path = '/home/gregory/Documents/mermaid_glap/random_data/Contains_glitch'
st = read_unidenfied_type(path)
print('Glitched',len(st))
mer_df1 = m.mermaid_df(st)

path = '/home/gregory/Documents/mermaid_glap/random_data/Contains_Twave'
st = read_unidenfied_type(path)
print('Contrains T waves',len(st))
mer_df2 = m.mermaid_df(st)

path = '/home/gregory/Documents/mermaid_glap/random_data/Contains_local'
st = read_unidenfied_type(path)
print('Local event',len(st))
mer_df3 = m.mermaid_df(st)

types=['Glitches and unidentified triggers','Twaves','Unidentified Event']
data_plots_un_type(mer_df1,mer_df2,mer_df3,types=types)
