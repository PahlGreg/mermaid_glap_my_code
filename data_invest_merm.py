#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 16:33:15 2026

@author: gregory


Overall this file aims to statistcally breakdown the selected dataset 
Code sections perpose
-----------------------------------------------
- code reads all identified mermaid sac files and then creates a pandas array from them 
- code that does the same for the guust dataset of picked arrivals 
- Code that adds regions to the mermaid dataset
- Code plots the statistic of entire dataset with all EQ mag and Arc dist

- data_plots: function creates plot of all mermaids indiviual breakdown according to a certain data
    2 options mag and gcarc
    Also plots the mean 
    Actual then plots for mag
- Code does data_plots for gcarc
- Code plots all mermaid surfacing recording location with bathymotry
- Code Info printed about dataset can be made into table 
- Code (obsolete in Unidentified_mer) Reads th unidentified record 
    then prints all days with more than 2 readings a day 
"""

import obspy
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from obspy.geodetics import FlinnEngdahl #for getting quake location
from obspy.core import UTCDateTime
from my_code.mer_data_invst_f import bathym


# Reading all the data in
st = read('data/galapagos/mermaid*/identified/sac/m*.sac')

#Turning all streams metadata into a pandas array 
'''
For Mer_record

Then for Guust picks

How to investigate say if you want the max magnitude then the region of that magnitude

> mer_df.loc[mer_df['mag'].idmax(),['magnitude','region']]

Then plots are made

'''

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
        "o": tr.stats.sac.get("o"),
        "stla": tr.stats.sac.get("stla"),
        "stlo": tr.stats.sac.get("stlo"),
        "stdp": tr.stats.sac.get("stdp"),
        "dist": tr.stats.sac.get("dist"),
        "evla": tr.stats.sac.get("evla"),
        "evlo": tr.stats.sac.get("evlo"),
        "gcarc": tr.stats.sac.get("gcarc"),
        "evdp": tr.stats.sac.get("evdp"),
        "mag": tr.stats.sac.get("mag"),
        'SNR (USER0)': tr.stats.sac.get('user0'),
        'CRITERION (USER1)': tr.stats.sac.get('user1')
    })

mer_df = pd.DataFrame(mer_record)

# %% Reading in guust data 

columes = ['idate',"iotime","ievt","kluster","stationcode","netw","comp",
"slat","slong","sdep","rlat","rlong","relv","nobst",'nobsa',"kpole"]

#for P Wave
GP = pd.read_csv("data/GALdata_picks/Data.GalP",
            header=None,skiprows=9,names=columes,
            delimiter = r'\s+')

GALP = GP.iloc[::5].copy() # df.iloc[start:stop:step]

GALP['ObsTT'] = GP.iloc[3:21735:5, 0].values
GALP['Sterr'] = GP.iloc[3:21735:5, 0].values

#for PkP Wave
GP = pd.read_csv("data/GALdata_picks/Data.GalPKP",
            header=None,skiprows=11,names=columes,
            delimiter = r'\s+')

GALPKP = GP.iloc[::5].copy() # df.iloc[start:stop:step]

# GALPKP['ObsTT'] = GPKP.iloc[3:21735:5, 0].values
# GALPKP['Sterr'] = GPKP.iloc[3:21735:5, 0].values

#for pP Wave
GP = pd.read_csv("data/GALdata_picks/Data.GalsmallpP",
            header=None,skiprows=10,names=columes,
            delimiter = r'\s+')

GALpP = GP.iloc[::5].copy() # df.iloc[start:stop:step]

# GALpP['ObsTT'] = GpP.iloc[3:21735:5, 0].values
# GALpP['Sterr'] = GpP.iloc[3:21735:5, 0].values

# %% Reading in unidentified mermaid data

st = read('data/galapagos/mermaid*/unidentified/sac/*.sac')

unmer_record=[]
for tr in st:
    unmer_record.append({
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
        "dist": tr.stats.sac.get("dist"),
        "evla": tr.stats.sac.get("evla"),
        "evlo": tr.stats.sac.get("evlo"),
        "gcarc": tr.stats.sac.get("gcarc"),
        "evdp": tr.stats.sac.get("evdp"),
        'SNR (USER0)': tr.stats.sac.get('user0'),
        'CRITERION (USER1)': tr.stats.sac.get('user1')
    })

unmer_df = pd.DataFrame(unmer_record)

# %% Adding a column with quake location
st = read('data/galapagos/mermaid*/identified/sac/m*.sac')

fe = FlinnEngdahl()
region=[]
for tr in st:
    region.append( fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla))
mer_df['region'] = region

# %% Adds guust picks to mermaid data
st = read('data/galapagos/mermaid*/identified/sac/m*.sac')
from obspy import Stream
def truncate(num, decimals=3):
    factor = 10 ** decimals
    return int(num * factor) / factor
mer_picks = GALP[GALP['netw']=='MERMAID']

st = Stream(
    tr for tr in st
    if round(tr.stats.sac.stla,3) in mer_picks['rlat'].values
    )


# %% Making plots of statistics and all data 
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

fig,ax = plt.subplots(1,2,figsize=(18,9))
bins=18

t1= mer_df['starttime'].min()
t2= mer_df['starttime'].max()


months = (t2.year - t1.year) * 12 + (t2.month - t1.month)
N=mer_df['mag'].count()
unique_N = len(mer_df['evla'].unique())
ax[0].text(
    0.6, 0.90,
    f'Event N = {N}\nUnique events N = {unique_N}\nMission duration = {months} months ',
    transform=ax[0].transAxes
    )
ax[0].hist(mer_df['mag'],bins=bins,
           linewidth=1,
           edgecolor='black',
           range=(4,8.5)) 
ax[0].set_title('Earthquake magnitude all mermaid')
ax[0].set_xlabel('magnitude Mw')
ax[0].set_ylabel('Counts')
ax[0].set_ylim(0,170)


bins=30
ax[1].hist(mer_df['gcarc'],bins=bins,
           linewidth=1,
           edgecolor='black',
           range=(0,180)) 
ticks = np.arange(0, 181, 60)
ax[1].set_xticks(ticks,[f'{t:.1f}° ' for t in ticks])
ax[1].set_title('Arc distance of each event recorded all mermaids')
ax[1].set_ylim(0,170)
plt.show()
# %%
'''
Creates a graph containign all mermaid eq magnitude total and individually
'''

from my_code.mer_data_invst_f import data_plots



data_plots(mer_df,dtype='magnitude',data='mag',bins=18)
# %%
'''
Repeating for distance from sensor in arc seconds 
'''
data_plots(mer_df, dtype='gcarc',unit='°',data='gcarc',bins=30, drange=(0,180))
# %% plotting map of mermaids
'''
Plots the mermaids with bathymotry data from 
www.naturalearthdata.com/
'''
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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


fig, ax = plt.subplots(figsize=(10,5),subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
    
#Obtaining the transform coords
data_crs = ccrs.PlateCarree()
ax.coastlines(linewidth=0.3)

stations = mer_df['station'].unique()


import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from matplotlib.patches import Patch
colours1 = [
    '#ffffff',  # white
    '#deebf7',
    '#c6dbef',
    '#9ecae1',
    '#6baed6',
    '#4292c6',
    '#2171b5',
    '#08306b'   # dark blue
]



contor = ['L_0','K_200', 'J_1000', 'I_2000', 'H_3000', 'G_4000', 'F_5000', 'E_6000']
contor_lab = ['0-200','200-1000', '1000-2000', '2000-3000', '3000-4000', '4000-5000', '5000-6000', '> 6000']
for i,bath in enumerate(contor):


    shpfile = f'random_data/ne_10m_bathymetry_all (copy)/ne_10m_bathymetry_{bath}.shp'
    shape_feature = cfeature.ShapelyFeature(
                                            shpreader.Reader(shpfile).geometries(),
                                            crs=ccrs.PlateCarree()
                                            )

    ax.add_feature(
        shape_feature,
        facecolor=colours1[i],
        linewidth=0.3,
        edgecolor='grey')
    
    shpfile = 'random_data/tectonicplates-master/PB2002_boundaries.shp'
    shape_feature = cfeature.ShapelyFeature(
                                            shpreader.Reader(shpfile).geometries(),
                                            crs=ccrs.PlateCarree()
                                            )
    ax.add_feature(
        shape_feature,
        linewidth=0.3,
        # transform=data_crs,
        facecolor='None',
        edgecolor='black',
        linestyle='--'
        )

    print(i)
    
land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                        edgecolor='face',
                                        facecolor=cfeature.COLORS['land'])
ax.add_feature(
    land_50m,
    facecolor='brown',
    edgecolor='grey')

    
# extent = [-105, -80, -10, 10]
# bath_im = bathym(ax,extent=extent,cbar_loc='right')
# ax.set_extent([-105, -80, -10, 10], crs=ccrs.PlateCarree())
for i,sensor in enumerate(stations):

    ses = ax.scatter(
        unmer_df.loc[unmer_df['station']==sensor,['stlo']],
        unmer_df.loc[unmer_df['station']==sensor,['stla']],
        color=colours[i],
        label=f'{sensor}',
        transform=data_crs,
        s=10,
        edgecolor='black',
        linewidth=0.4,
        zorder=100
    )
    ax.scatter(
        unmer_df.loc[unmer_df['station']==sensor,['stlo']].iloc[0],
        unmer_df.loc[unmer_df['station']==sensor,['stla']].iloc[0],
        color=colours[i],
        label='_nolegend_',
        transform=data_crs,
        s=40,
        marker='*',
        edgecolor='black',
        linewidth=0.7,
        zorder=100
    )

leg1 = ax.legend(title='Mermaid',
          ncol=2,
          fontsize=8,
          title_fontsize=7,
          markerscale=2
          )
ax.add_artist(leg1)

depth_legend = [
    Patch(facecolor=colours1[i],
          edgecolor='grey',
          label=f'{bath} m')
    for i, bath in enumerate(contor_lab)
]
ax.legend(
    handles=depth_legend,
    title='Ocean depth',
    loc='upper left',
    ncol=2,
    fontsize=5,
    title_fontsize=7
    )
plt.title('Mermaid unidentified trigger location with ocean depth for entire deployment')
plt.show()

# %%
'''
Info about the mermaid mission
'''
print(mer_df['starttime'].min(), ' first mission transmission')
print(mer_df['endtime'].max(), ' last mission transmission')
print(mer_df['mag'].min(), '')

# %% Plot of trigger days for mermaids
'''
THen counting the amount of records per day
for unidentified
'''


unmer_df['date'] = unmer_df['starttime'].apply(lambda x: x.date())
trig_date = unmer_df.groupby(['station','date']).size()


results = []

for sensor in stations:
    #makes a seperate data fram that just has the counts 
    counts = (
        unmer_df[unmer_df['station'] == sensor]
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

print(results_df.to_string(index=False))

# %% testing reciever_loc_all

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

from my_code.mer_data_invst_f import reciever_loc_all
title='Unidentified mermaid record with rythmic rumbling 2015-01-20 to 2015-01-25'
unmer_n = unmer_df[unmer_df['station'].isin([19,21,22,24,25,26])] #needc to select the stations within that timefram maybe change
int_unmer_n = unmer_n[
    (unmer_n['starttime'] >= '2015-01-20') &
    (unmer_n['starttime'] < '2015-01-30')
]
reciever_loc_all(int_unmer_n, title=title)


    