#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 14:28:31 2026

@author: gregory
"""
import obspy
from obspy import Stream, Trace
from obspy.signal import cross_correlation
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
import seaborn as sns
from scipy.signal import find_peaks 

sys.path.append('/home/gregory/Documents/mermaid_glap')


from matplotlib.ticker import MultipleLocator
from my_code.mer_plot_f import basic_proc

'''
SUMMARY
CODE creates function to plot section polots either abolute time or relative to 0
Also contains option/ still some code to window and limit all amplites to aorund a set period currently 10-75 seconds 
THIS WAS AIMED AT ANALYSISING THE 20S period SIGNALS THAT ARE NOW ASSUMED TO BE AN AIRGUN

OTHER CODE 
- Code to further analysis the 20hz signal: 
    - Creates a plot of location with amplitude averaged over 3 peaks 
'''

# %%

def section_plot_T0(st, st_wind ,startdate, enddate,sharey=False, freq_min=0.1,freq_max=10,normalise=False):
    '''
    Info 
    Currenly the max value is set by the filtered noise within first 10-50 seconds max value of all streams 
    Off set is also determined by the maximum amplitude multiplied by an amount
    '''

    n = len(st)
    fig, ax =  plt.subplots(figsize=(15,1*n),sharey=sharey)
    basic_proc(st)


    filter_method = 'bandpass'

    st = st.filter(filter_method, freqmax = freq_max, freqmin = freq_min)
    
    
    #normalising

    # # pick the reference trace (e.g. by index or by station code)
    # ref_trace = st[0]  # 
    
    # ref_max = np.max(np.abs(ref_trace.data))
    
    # for tr in st:
    #     tr.data = tr.data / ref_max
    
    starttime_all = min(tr.stats.starttime for tr in st)
    endtime_all = max(tr.stats.endtime for tr in st)
    stations = sorted(set(tr.stats.station for tr in st))

    offset = 0
    spacing= max(np.max(np.abs(tr.data)) for tr in st_wind) * 1.5
    
    for tr,tr1 in zip(st,st_wind):
        # spacing = (max(tr.data))+ spacing# not sure i agree with this
        maximum = max(tr1.data)
        minimum = min(tr1.data)
        tr.data = np.clip(tr.data, minimum, maximum)
        times = tr.times()
        ax.plot(times,tr.data + offset, 'darkblue', linewidth=0.7)
        ax.text(times[0],offset,f'{str(tr.stats.starttime)[:14]}.M{str(tr.stats.station)}', fontsize=8, va='center', ha='right')
        ax.set_ylim
        offset += spacing
        print(max(tr.data))
        ax.set_yticks([])
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        # Grid lines for both
        ax.grid(which='major', axis='x', linewidth=0.8, color='gray')
        ax.grid(which='minor', axis='x', linewidth=0.4, color='lightgray', linestyle='--')


    ax.set_xlabel("Time (s)")
    if normalise==True:
        norm='+ normalise '
    else:
        norm=''
    ax.set_title(f'Seismic section | Time frame={str(starttime_all)[:16]} - {str(endtime_all)[:16]}  |\n station={stations} |  Demean + Detrend + taper {norm}| filtering method= {filter_method} | freq = {freq_min:.1f}-{freq_max:.1f} Hz')

# %%

def section_plot_Tabs_windowed(st, st_wind ,startdate, enddate,sharey=False, freq_min=0.1,freq_max=10,normalise=False):
    '''
    This code plots a secon plot relative to actual starttime and then clipps section
    Info 
    Currenly the max value is set by the filtered noise within first 10-50 seconds max value of all streams 
    Off set is also determined by the maximum amplitude multiplied by an amount
    
    Has option to then window by the first 70 seconds max (usefgul looking at noise and t waves)
    
    OUTPUT
    Matplotlib section plot actual timesince first starttime 
    '''

    n = len(st)
    fig, ax =  plt.subplots(figsize=(15,1*n),sharey=sharey)
    basic_proc(st)


    filter_method = 'bandpass'

    st = st.filter(filter_method, freqmax = freq_max, freqmin = freq_min)
    
    
    # normalising
    if normalise:
        st.normalize(global_max=False)
    # # pick the reference trace (e.g. by index or by station code)
    # ref_trace = st[0]  # 
    
    # ref_max = np.max(np.abs(ref_trace.data))
    
    # for tr in st:
    #     tr.data = tr.data / ref_max
    
    starttime_all = min(tr.stats.starttime for tr in st)
    endtime_all = max(tr.stats.endtime for tr in st)
    stations = sorted(set(tr.stats.station for tr in st))


    offset = 0
    spacing= max(np.max(np.abs(tr.data)) for tr in st_wind) * 1.5
    
    minimum = min(np.min((tr.data)) for tr in st_wind)
    
    for tr,tr1 in zip(st,st_wind):
        # spacing = (max(tr.data))+ spacing# not sure i agree with this
        maximum = max((tr1.data))
        minimum = min((tr1.data))

        tr.data = np.clip(tr.data, minimum, maximum)
        times = tr.times(reftime=starttime_all)
        ax.plot(times,tr.data + offset, 'darkblue', linewidth=0.7)
        ax.text(times[0],offset,f'{str(tr.stats.starttime)[:14]}.M{str(tr.stats.station)}', fontsize=8, va='center', ha='right')
        offset += spacing
        ax.set_yticks([])
        
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        # Grid lines for both
        ax.grid(which='major', axis='x', linewidth=0.8, color='gray')
        ax.grid(which='minor', axis='x', linewidth=0.4, color='lightgray', linestyle='--')


    ax.set_xlabel("Time (s)")
    if normalise==True:
        norm='+ normalise '
    else:
        norm=''
    ax.set_title(f'Seismic section | Time frame={str(starttime_all)[:16]} - {str(endtime_all)[:16]} | station={stations} | \n  Demean + Detrend + taper {norm}| filtering method= {filter_method} | freq = {freq_min:.1f}-{freq_max:.1f} Hz | max amplitude limited')

   
    return
    
    
def section_plot_Tabs(st ,startdate, enddate,sharey=False, freq_min=0.1,freq_max=10,normalise=False):
    '''
    Same as above but 0 is not startime of all traces
    Info 
    Currenly the max value is set by the filtered noise within first 10-50 seconds max value of all streams 
    Off set is also determined by the maximum amplitude multiplied by an amount
    
    
        '''

    n = len(st)
    fig, ax =  plt.subplots(figsize=(15,1*n),sharey=sharey)
    basic_proc(st)


    filter_method = 'bandpass'

    st = st.filter(filter_method, freqmax = freq_max, freqmin = freq_min)
    
    
    # normalising
    if normalise:
        st.normalize(global_max=False)
    # # pick the reference trace (e.g. by index or by station code)
    # ref_trace = st[0]  # 
    
    # ref_max = np.max(np.abs(ref_trace.data))
    
    # for tr in st:
    #     tr.data = tr.data / ref_max
    
    starttime_all = min(tr.stats.starttime for tr in st)
    endtime_all = max(tr.stats.endtime for tr in st)
    stations = sorted(set(tr.stats.station for tr in st))


    offset = 0
    spacing= max(np.max(np.abs(tr.data)) for tr in st) * 1.5
    
    
    for tr in st:
        # spacing = (max(tr.data))+ spacing# not sure i agree with this

        times = tr.times(reftime=starttime_all)
        ax.plot(times,tr.data + offset, 'darkblue', linewidth=0.7)
        ax.text(times[0],offset,f'{str(tr.stats.starttime)[:14]}.M{str(tr.stats.station)}', fontsize=8, va='center', ha='right')
        offset += spacing
        ax.set_yticks([])
        
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        # Grid lines for both
        ax.grid(which='major', axis='x', linewidth=0.8, color='gray')
        ax.grid(which='minor', axis='x', linewidth=0.4, color='lightgray', linestyle='--')


    ax.set_xlabel("Time (s)")
    if normalise==True:
        norm='+ normalise '
    else:
        norm=''
    ax.set_title(f'Seismic section | Time frame={str(starttime_all)[:16]} - {str(endtime_all)[:16]}  |\n station={stations} |  Demean + Detrend + taper {norm}| filtering method= {filter_method} | freq = {freq_min:.1f}-{freq_max:.1f} Hz')

   
    return
    

# %%code that pltos a record relative to each time 0
# Also clips data by the max in the first 30 seconds 
st = read('data/galapagos/mermaid*/*identified/sac/m*.*.sac')

startdate = input('Enter a date for start of timeframe in YYYYMMDDTHH (hour optional): ') or '20150124T05' # the or is defults

enddate = input('Enter end date: ') or '20150124T06'

st = Stream(
    tr for tr in st
    if UTCDateTime(tr.stats.starttime) >= UTCDateTime(startdate) 
    and UTCDateTime(tr.stats.endtime) <= UTCDateTime(enddate) 
    # and tr.stats.station in stations
    )

freq_max=10
freq_min=5
sharey=False
normalise = False
# Getting max amp but windowing the 10-50 seconds 
'''
Currently doesnt do this heres code
for tr1,tr in zip(st_wind,st_filt):
    tr1.trim(tr.stats.starttime + 10, tr.stats.starttime + 75)
    maximum = max(tr1.data)
    minimum = min(tr1.data)
    tr.data = np.clip(tr.data, minimum, maximum)
'''
st_wind = st.copy()
basic_proc(st_wind)


filter_method = 'bandpass'

st_wind = st_wind.filter(filter_method, freqmax = freq_max, freqmin = freq_min)
# for tr in st_wind:
#     tr.trim(tr.stats.starttime + 10, tr.stats.starttime + 75)
    
    

# section_plot_T0(st,st_wind,startdate,enddate,sharey=sharey,freq_min=freq_min,freq_max=freq_max)
section_plot_Tabs_windowed(st,st_wind,startdate,enddate,sharey=sharey,freq_min=freq_min,freq_max=freq_max,normalise=normalise)

plt.show()
# %% Nonclipped
from my_code.commands.import_iris_data import iris_import
st = read('data/galapagos/mermaid*/*identified/sac/m*.*.sac')

startdate = input('Enter a date for start of timeframe in YYYYMMDDTHH (hour optional): ') or '20150503T05' # the or is defults

enddate = input('Enter end date: ') or '20150503T06'

st = Stream(
    tr for tr in st
    if UTCDateTime(tr.stats.starttime) >= UTCDateTime(startdate) 
    and UTCDateTime(tr.stats.endtime) <= UTCDateTime(enddate) 
    # and tr.stats.station in stations
    )

st = iris_import(st)
freq_max=5
freq_min=0.5
sharey=False
normalise = True
# Getting max amp but windowing the 10-50 seconds 
    

# section_plot_T0(st,st_wind,startdate,enddate,sharey=sharey,freq_min=freq_min,freq_max=freq_max)
section_plot_Tabs(st,startdate,enddate,sharey=sharey,freq_min=freq_min,freq_max=freq_max,normalise=normalise)

plt.show()

# %% Checking absolutles of window around noise

from my_code.mer_plot_f import multiplot_filt
st = read('data/galapagos/mermaid*/*identified/sac/m2*.20150120*.sac')

st_filt = st.copy()

#De trend and demean
basic_proc(st_filt)

freq_maximum = 10
freq_minimum =5
#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'
st_filt = st_filt.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

st_wind = st_filt.copy()
for tr1,tr in zip(st_wind,st_filt):
    tr1.trim(tr.stats.starttime + 10, tr.stats.starttime + 75)
    maximum = max(tr1.data)
    minimum = min(tr1.data)
    tr.data = np.clip(tr.data, minimum, maximum)

multiplot_filt(st,st_filt,filt_type='bandpass', freq_max = freq_maximum, freq_min = freq_minimum,sharey=True)
plt.show




# %%Measuring max amplitude of signal 
#Temp investigating find peak
# set to 10 seconds appart to avoid same peak 
import cartopy.crs as ccrs

'''
All this is hardcoded for this one period 
'''
def find_average_of_3_peaks(tr,interval=10):
    peaks, peak_prop=find_peaks(tr.data, distance=interval*20, height=-np.inf) # * 20 as sampling rate to get peak every 10 seconds 
    
    heights = peak_prop['peak_heights']
    top3_height_idx = np.argsort(heights)[-3:][::-1]  # descending order (largest first)
    
    top3_peaks_index = peaks[top3_height_idx] # this gives total tr.data index
    max_3_heights = tr.data[top3_peaks_index]
    avg_max = np.mean(max_3_heights)
    
    return avg_max, top3_peaks_index
# %% Plotting map of max


from my_code.mer_data_invst_f import reciever_loc_all_data, mermaid_df
st = read('data/galapagos/mermaid*/*identified/sac/m2*.20150120*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m19.20150120*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150124T13*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150124T14*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150117T18*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150118T03*.sac')


# To remove event 

for tr in st:
    tr.trim(tr.stats.starttime + 10, tr.stats.starttime + 75)
starttime_all = min(tr.stats.starttime for tr in st)
endtime_all = max(tr.stats.endtime for tr in st)

freq_max=10
freq_min=5
filter_method = 'bandpass'

# Maybe use this for ones with arrivals i shoudl manually pick them 
# st_wind = st.copy()
# basic_proc(st_wind)
# st_wind = st_wind.filter(filter_method, freqmax = freq_max, freqmin = freq_min)
# for tr in st_wind:
#     tr.trim(tr.stats.starttime + 10, tr.stats.starttime + 60)

basic_proc(st)
st.filter(filter_method, freqmax = freq_max, freqmin = freq_min)

mer_df=mermaid_df(st)
mer_df['date'] = mer_df['starttime'].apply(lambda x: x.date())

# mer_df["max_amplitude"] = [find_average_of_3_peaks(tr)[0] for tr in st]
mer_df["max_amplitude"] = [max(tr.data) for tr in st]


title= f'Mermaid record triggers location with periodic signals from {str(starttime_all)[:19]} to {str(endtime_all)[:19]},\n max amp is averaged over 3 peaks for 10s-70s of the trigger'

ax,fig = reciever_loc_all_data(mer_df,title=title,show=False)

# Plotting mermaid that didnt see event 
st= read('data/galapagos/mermaid*/*identified/sac/m10*.20150120*.sac')

tr=st[0]
new_pt= ax.scatter(
    tr.stats.sac.stlo,
    tr.stats.sac.stla,
    transform=ccrs.PlateCarree(),   # <-- tells cartopy these are lon/lat, not projected coords
    s=150,
    c='white',
    marker='o',
    edgecolors='k',
    zorder=6
)
# Grab the existing legend's handles/labels before removing it
old_legend = ax.get_legend()
handles = old_legend.legend_handles
labels = [t.get_text() for t in old_legend.get_texts()]
old_legend.remove()

# Add the new point's handle/label
handles.append(new_pt)
labels.append('10\n(no signal)')

new_legend = ax.legend(handles, labels, title='Station', loc='upper right')
ax.add_artist(new_legend)

fig.canvas.draw()
fig

plt.show()
# Plotting stations that didnt see

# st = read('data/galapagos/mermaid*/*identified/sac/m*.201501*.sac')

# mer_df2 = mermaid_df(st)
# missing_stations = set(mer_df2['station']) - set(mer_df['station'])
 
# %% Checking the spacing between using max peak  then outputs the spacing between

st = read('data/galapagos/mermaid*/*identified/sac/m2*.20150120*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m19.20150120*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150124T13*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150124T14*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150117T18*.sac')
st += read('data/galapagos/mermaid*/*identified/sac/m*.20150118T03*.sac')


# To remove event 

for tr in st:
    tr.trim(tr.stats.starttime + 10, tr.stats.starttime + 75)
    
starttime_all = min(tr.stats.starttime for tr in st)
endtime_all = max(tr.stats.endtime for tr in st)

freq_max=10
freq_min=5
filter_method = 'bandpass'

# Maybe use this for ones with arrivals i shoudl manually pick them 
# st_wind = st.copy()
# basic_proc(st_wind)
# st_wind = st_wind.filter(filter_method, freqmax = freq_max, freqmin = freq_min)
# for tr in st_wind:
#     tr.trim(tr.stats.starttime + 10, tr.stats.starttime + 60)

basic_proc(st)
st.filter(filter_method, freqmax = freq_max, freqmin = freq_min)
for tr in st:
    tr.plot()

mer_df=mermaid_df(st)
mer_df['date'] = mer_df['starttime'].apply(lambda x: x.date())

mer_df["max_amplitude"] = [find_average_of_3_peaks(tr)[0] for tr in st]

mer_df['max_index']= [np.sort(find_average_of_3_peaks(tr)[1]) for tr in st]

for  i,j in enumerate(mer_df['max_index']):
    dif=[]
    dif.append(
        (j[1]-j[0])/20)
    dif.append(
        (j[2]-j[1])/20)
    dif.append(
        (j[2]-j[0])/40)

    print(f'm{mer_df["station"][i]}.{str(mer_df["starttime"][i])[:10]}| has interval time: {np.mean(dif)}s')

