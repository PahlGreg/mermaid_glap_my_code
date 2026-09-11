#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 13:17:41 2026

@author: gregory

Reads guust picks, putting them into a pandas data fram including all lines 

- source_loc_mag: function plots the location of all earthquakes with mag colour noted in a dataset
    Has to be changed between guust dataset and mermaid due to headers
    Can also plot just for Americas
- source_loc_dp: same as above but with depth of quake
REMEMBER YOU CAN ADD TITLE AFTER
- CMAP created
- reciever_loc: plot of receiver locations in dataset 
    Again change between guust and mermaid
    
- Code that creates 4 plots of sensors easier to see using function for glap and americas 

pltos reciever locations 
Plots reciever location
"""

# readding and plotting guusts picks


from obspy.geodetics import FlinnEngdahl
import obspy.signal
import obspy
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader


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
GPKP = pd.read_csv("data/GALdata_picks/Data.GalPKP",
            header=None,skiprows=11,names=columes,
            delimiter = r'\s+')

GALPKP = GPKP.iloc[::5].copy() # df.iloc[start:stop:step]

# GALPKP['ObsTT'] = GPKP.iloc[3:21735:5, 0].values
# GALPKP['Sterr'] = GPKP.iloc[3:21735:5, 0].values

#for pP Wave
GpP = pd.read_csv("data/GALdata_picks/Data.GalsmallpP",
            header=None,skiprows=10,names=columes,
            delimiter = r'\s+')

GALpP = GpP.iloc[::5].copy() # df.iloc[start:stop:step]

# GALpP['ObsTT'] = GpP.iloc[3:21735:5, 0].values
# GALpP['Sterr'] = GpP.iloc[3:21735:5, 0].values

# %% Function to plot source location
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader

'''
Currrenly adjused for actual dataset not guust

also changed for mag
'''

from my_code.mer_data_invst_f import source_loc_mag

source_loc_mag(GpP)
# %%






source_loc_mag(mer_df,world=True)
# %%

from my_code.mer_data_invst_f import source_loc_dp



source_loc_dp(mer_df)
# %%
'''
Source for picked mermaids guust dataset
'''
GALP_mer = GALP[GALP['netw']=='MERMAID']
n = source_loc_dp(GALP_mer)
plt.title(f'Plot of earthquake locations & depth detected by MERMAID that have P wave picks, N = {n}')
plt.show()

# %%Custon cmap centered on 0


colors = ["lightblue", "grey", "darkorange"]
cmap = LinearSegmentedColormap.from_list("mycmap", colors)







# %%

from my_code.mer_data_invst_f import reciever_loc

#Currently broken for some reason both are
reciever_loc(GALP)

#ploting map of unidentified mermaid locations when found
reciever_loc(unmer_df)


# %% Plots map of reciver and close up for mermaid

   #Plotting entire stations
fig, ax = plt.subplots(2,2,figsize=(16, 8),
                   subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
    
#Obtaining the transform coords
data_crs = ccrs.PlateCarree()
for a in ax.flat:
    a.coastlines(linewidth=0.3)

ax[0,0].set_extent([-180, -30, -60, 60], crs=ccrs.PlateCarree()) # Limiting to world
ax[0,1].set_extent([-180, -30, -60, 60], crs=ccrs.PlateCarree()) # Limiting to world
ax[1,0].set_extent([-105, -80, -10, 10], crs=ccrs.PlateCarree()) # Limiting to Galap
ax[1,1].set_extent([-105, -80, -10, 10], crs=ccrs.PlateCarree()) # Limiting to Galap

# Plot points
mermaid_lon = GALP[GALP['netw'] == 'MERMAID']['rlong']
mermaid_lat = GALP[GALP['netw'] == 'MERMAID']['rlat']

#Norm to calculate colour map
norm = TwoSlopeNorm(vmin=GALP['relv'].min(),  # negative minimum
    vcenter=0,
    vmax=GALP['relv'].max()
)

# Depth data
land_rloc = ax[0,0].scatter(GALP['rlong'],GALP['rlat'],
                    s=10,transform=data_crs,
                    c = GALP['relv'], cmap='viridis',norm=norm,
                    edgecolors='k',linewidth=0.1)
ax[0,0].set_title('Depth of Sensor in record')

#Type of station
rloc = ax[0,1].scatter(GALP['rlong'],GALP['rlat'],
                    s=10,transform=data_crs,
                    edgecolors='k',linewidth=0.1
                    )
                 


    
ax[0,1].set_title('Sensor type')

#Norm to calculate colour map 
#New for mermaids with max 0
norm = TwoSlopeNorm(
    vmin=GALP['relv'].min(),  # negative minimum
    vcenter=-1.5,
    vmax=0
)
    
#Depth of station zoomed into galap
merm = ax[1,0].scatter(GALP['rlong'],GALP['rlat'],
                    s=10,transform=data_crs,
                    c = GALP['relv'], cmap='winter', norm= norm,
                    edgecolors='k',linewidth=0.2)

#Type zoomed into galap shows mermaid and normal
ax[1,1].scatter(GALP['rlong'],GALP['rlat'],
                    s=10,transform=data_crs,color='black', label='Other',
                    edgecolors='k',linewidth=0.2)
ax[1,1].scatter(mermaid_lon,mermaid_lat,
                    s=10,transform=data_crs,color='lightgreen', label ='mermaid',
                    edgecolors='k',linewidth=0.2)
ax[1,1].legend()
# Takes all GALP thats not NETW == MERMAID and then obtains all unique GALP with locaiton and code
# df = GALP.loc[
#     GALP['netw'] != 'MERMAID', 
#     ['rlong','rlat','stationcode','netw']
#     ].drop_duplicates()

# for i in range(len(df)):
#     ax[1,1].annotate(df['stationcode'].iloc[i],
#                      xy=(df['rlat'].iloc[i],df['rlong'].iloc[i]),
#                      textcoords='offset points',
#                      xytext=(3, 3),
#                      transform=data_crs,
#                      )


# mermaid_loc = plt.scatter(mermaid_lon,mermaid_lat,
#                     s=10,transform=data_crs,color='y')
fig.colorbar(land_rloc,ax=ax[0,0],shrink=0.9,label='Depth (km)')
fig.colorbar(merm,ax=ax[1,0],shrink=0.9,label='Depth (km)')


for a in ax.flat:
    gl = a.gridlines(
    draw_labels=True,
    linewidth=0.5,
    color='gray',
    alpha=0.5,
    linestyle='--'
    )
    gl.top_labels = False
    gl.right_labels = False

plt.tight_layout()
plt.show()

# -----------------------------------------
# The graphs are limited to reciever location initially




# %%
# Takes all GALP thats not NETW == MERMAID and then obtains all unique GALP with locaiton and code
df = GALP.loc[
    GALP['netw'] != 'MERMAID', 
    ['rlong','rlat','relv','stationcode','netw']
    ].drop_duplicates()

df = GALP.loc[
    GALP['netw'] == 'MERMAID', 
    ['rlong','rlat','relv','stationcode','netw']
    ].drop_duplicates()

fig, ax = plt.subplots(subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
    
#Obtaining the transform coords
data_crs = ccrs.PlateCarree()
ax.coastlines(linewidth=0.3)
    
ax.set_extent([-105, -80, -10, 10], crs=ccrs.PlateCarree())

ax.scatter(df['rlong'],df['rlat'],
                    s=10,transform=data_crs,
                    c = df['stationcode'], cmap='viridis',norm=norm,
                    edgecolors='k',linewidth=0.1)




