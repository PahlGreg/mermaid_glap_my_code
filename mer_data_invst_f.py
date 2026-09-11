#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 16:15:31 2026

@author: gregory
"""
'''
Reads guust picks, putting them into a pandas data fram including all lines 

This also works for the entire dataset particaully for the plotting

- source_loc_mag: function plots the location of all earthquakes with mag colour noted in a dataset
    Has to be changed between guust dataset and mermaid due to headers
    Can also plot just for Americas
- source_loc_dp: same as above but with depth of quake
REMEMBER YOU CAN ADD TITLE AFTER
- CMAP created
- reciever_loc: plot of receiver locations in dataset 
    Again change between guust and mermaid
    
- Code that creates 4 plots of sensors easier to see using function

'''


from obspy.geodetics import FlinnEngdahl
import obspy.signal
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from pathlib import Path
from datetime import datetime
import os
from my_code.mer_plot_f import spectrogram_plot_uni, mermaid_df
import rasterio
from matplotlib.colors import Normalize

# %% Plot bathm

def bathym(ax,leg_loc='upper left',
           ncol=2,
           fontsize=5,
           title_fontsize=7):
    
    #Obtaining the transform coords
    ax.coastlines(linewidth=0.3)
    
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
            edgecolor='grey',
            zorder=1)
        
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
            linestyle='--',
            zorder=2
            )
    
        
    land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
                                            edgecolor='face',
                                            facecolor=cfeature.COLORS['land'])
    ax.add_feature(
        land_50m,
        facecolor='brown',
        edgecolor='grey')
    
    #legend
    depth_legend = [
        Patch(facecolor=colours1[i],
              edgecolor='grey',
              label=f'{bath} m')
        for i, bath in enumerate(contor_lab)
    ]
    legend = ax.legend(
        handles=depth_legend,
        title='Ocean depth',
        loc=leg_loc,
        ncol=ncol,
        fontsize=fontsize,
        title_fontsize=title_fontsize
        )
    
    return legend

# %% Bathym using gebco


# def bathym(ax, extent,
#            cmap_name='Blues',
#            vmin=0,
#            vmax=6000,
#            cbar_loc='right',
#            fontsize=5,
#            title_fontsize=7):

#     ax.coastlines(linewidth=0.3)

# #     # --- read the bathymetry tiff ---
#     with rasterio.open('random_data/gebco_bath_glap/gebco_2026_n10.0_s-10.0_w-105.0_e-80.0_geotiff.tif') as src:        
#         # coordinates: left, bottom, right, top (in the file's CRS — usually lon/lat for GEBCO)
#         window = rasterio.windows.from_bounds(extent[0],extent[1] ,extent[2], extent[3], transform=src.transform)
        
#         data = src.read(1, window=window)
        
#         # updated transform/bounds for the clipped window — use these for extent, not the original src.bounds
#         clipped_transform = src.window_transform(window)
#         left, bottom, right, top = rasterio.windows.bounds(window, src.transform)

#     # Most bathymetry/elevation tiffs store ocean as negative values
#     # (elevation below sea level). Flip sign to get positive depth,
#     # and mask out land (positive elevation / negative depth).
#     depth = -data
#     depth = np.where(depth < 0, np.nan, depth)

#     cmap = plt.get_cmap(cmap_name)
#     norm = Normalize(vmin=vmin, vmax=vmax)

#     im = ax.imshow(
#         depth,
#         origin='upper',
#         extent=[left, right, bottom, top],
#         transform=ccrs.PlateCarree(),
#         cmap=cmap,
#         # norm=norm,
#         zorder=1,
#         # interpolation='bilinear'
#     )

#     # --- tectonic plate boundaries (unchanged) ---
#     shpfile = 'random_data/tectonicplates-master/PB2002_boundaries.shp'
#     shape_feature = cfeature.ShapelyFeature(
#         shpreader.Reader(shpfile).geometries(),
#         crs=ccrs.PlateCarree()
#     )
#     ax.add_feature(
#         shape_feature,
#         linewidth=0.3,
#         facecolor='None',
#         edgecolor='black',
#         linestyle='--',
#         zorder=2
#     )

#     # --- land (unchanged) ---
#     land_50m = cfeature.NaturalEarthFeature('physical', 'land', '50m',
#                                              edgecolor='face',
#                                              facecolor=cfeature.COLORS['land'])
#     ax.add_feature(
#         land_50m,
#         facecolor='brown',
#         edgecolor='grey')

#     # # --- colorbar instead of patch legend ---
#     # cbar = plt.colorbar(
#     #     im,
#     #     ax=ax,
#     #     orientation='vertical' if cbar_loc in ('right', 'left') else 'horizontal',
#     #     location=cbar_loc,
#     #     shrink=0.6,
#     #     pad=0.05
#     # )
#     # cbar.set_label('Ocean depth (m)', fontsize=title_fontsize)
#     # cbar.ax.tick_params(labelsize=fontsize)
    
#     return im
# %% source_loc_mag plot

def source_loc_mag(GALP,world=True):
    
    fig = plt.figure(figsize=(20, 10))
    ax = plt.axes(projection=ccrs.Mollweide(central_longitude=180))
    
    #Obtaining the transform coords
    data_crs = ccrs.PlateCarree()
    
    '''
    Plotting plate boundaries form Peter Bird 2003 / PB2002 dataset
    '''
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
    
    if 'evlo' in GALP.columns:
        long= 'evlo'
        lat = 'evla'
        
    else:    
        raise KeyError("Guust data doesnt contain magnitude")

    

    if world == True:
        ax.set_global()
        n=GALP[lat].nunique()
        plt.title(f"Plot of earthquake locations & magnitudes detected by Mermaids, N = {n}")

        
    else:
        ax.set_extent([-120, -20, -60, 60],
                      crs=ccrs.PlateCarree()
                      )
        plt.title("lot of earthquake locations & magnitudes detected by Mermaids in Americas")

        
    ax.coastlines(linewidth=0.3)
    # Plot points
    eqloc = plt.scatter(GALP[long],
              GALP[lat],
              s=30,c=GALP['mag'],cmap='gist_heat_r',
              transform=data_crs,
              edgecolors='k',linewidth=0.1,
              marker='*')
    plt.scatter(-90.7,-0.006,transform=data_crs,s=20,marker='v',color='r',)
    plt.colorbar(eqloc,shrink=0.9,label='magnitude')

    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.5,
        color='gray',
        alpha=0.5,
        linestyle='--'
        )
    # Customize label appearance and visibility
    gl.inline_labels = True
    gl.x_inline = True
    gl.top_labels = False       # Turn off labels at the top
    gl.right_labels = False  
    
    plt.show()
     
# %% Source location with depth colour map

def source_loc_dp(GALP,world=True,log=False):
    
    '''
    Currently for Guust mermaid
    '''
    
    if 'evlo' in GALP.columns:
        long= 'evlo'
        lat = 'evla'
        depth = 'evdp'

        
    else:    
        long= 'slong'
        lat = 'slat'
        depth = 'sdep'

    
    fig = plt.figure(figsize=(20, 10))
    ax = plt.axes(projection=ccrs.Mollweide(central_longitude=180))
    
    #Obtaining the transform coords
    data_crs = ccrs.PlateCarree()
    
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
    
    if world == True:
        ax.set_global()
        n=GALP[lat].nunique()
        plt.title(f"Plot of earthquake locations & depth detected by Mermaids, N = {n}")

        
    else:
        ax.set_extent([-120, -20, -60, 60],
                      crs=ccrs.PlateCarree()
                      )
        plt.title("lot of earthquake locations & depth detected by Mermaids in Americas")

        
    ax.coastlines(linewidth=0.3)
    
    if log == True:
        # Plot points
        eqloc = plt.scatter(GALP[long],
                  GALP[lat],
                  s=30,c=GALP[depth],cmap='cividis_r',
                  transform=data_crs,
                  edgecolors='k',linewidth=0.1,
                  marker='*',norm='log')
        plt.scatter(-90.7,-0.006,transform=data_crs,s=20,marker='v',color='r',)

        cbar=plt.colorbar(eqloc,shrink=0.9,label='Depth (km)',ticks=[1, 10, 100, 600])
        cbar.set_ticklabels(['1', '10', '100', '600'])
    else:
            # Plot points
        eqloc = plt.scatter(GALP[long],
                  GALP[lat],
                  s=30,c=GALP[depth],cmap='cividis_r',
                  transform=data_crs,
                  edgecolors='k',linewidth=0.1,
                  marker='*')
        plt.scatter(-90.7,-0.006,transform=data_crs,s=20,marker='v',color='r',)
        cbar=plt.colorbar(eqloc,shrink=0.9,label='Depth (km)')

    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.5,
        color='gray',
        alpha=0.5,
        linestyle='--'
        )
    # Customize label appearance and visibility
    gl.inline_labels = True
    gl.x_inline = True
    gl.top_labels = False       # Turn off labels at the top
    gl.right_labels = False  
    
    return n

# %% Receiver loc map
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
'''
PLot of recievers that located a earthqayke 

Produces 4 plots some of gloval location then some of local

colour is depth of sensor 
 
'''

def reciever_loc(GALP):
    
    #Plotting entire stations
    fig, ax = plt.subplots(2,5,figsize=(20, 10),
                       subplot_kw={'projection': ccrs.Mollweide(central_longitude=180)})
        
    #Obtaining the transform coords
    data_crs = ccrs.PlateCarree()
    for a in ax.flat:
        a.coastlines(linewidth=0.3)
    
    ax[0,0].set_extent([-180, -30, -60, 60], crs=ccrs.PlateCarree()) # Limiting to world
    ax[0,1].set_extent([-180, -30, -60, 60], crs=ccrs.PlateCarree()) # Limiting to world
    ax[1,0].set_extent([-105, -80, -10, 10], crs=ccrs.PlateCarree()) # Limiting to Galap
    ax[1,1].set_extent([-105, -80, -10, 10], crs=ccrs.PlateCarree()) # Limiting to Galap

    # Plot points
    
    if 'stlo' in GALP.columns:
        long= 'stlo'
        lat = 'stla'
        depth = 'stdp'
        network='network'
        station='station'
        norm = TwoSlopeNorm(
            vmin=GALP[depth].min(),  # negative minimum
            vcenter=-1.5,
            vmax=0
        )

        
    else:    
        long= 'rlong'
        lat = 'rlat'
        depth = 'relv'
        network='netw'
        station='stationcode'
        norm = TwoSlopeNorm(
            vmin=GALP[depth].min(),  # negative minimum
            vcenter=0,
            vmax=GALP[depth].max()
        )
        
    mermaid_lon = GALP[GALP[network] == 'MERMAID'][long]
    mermaid_lat = GALP[GALP[network] == 'MERMAID'][lat]
    
    # Depth data
    land_rloc = ax[0,0].scatter(GALP[long],GALP[lat],
                        s=20,transform=data_crs,
                        c = GALP[depth], cmap='viridis',norm=norm,
                        edgecolors='k',linewidth=0.1, marker='^')
    n = GALP[station].nunique()
    ax[0,0].set_title(f'Depth of Sensor in record, N={n}')
    
    #Type of station
    rloc = ax[0,1].scatter(GALP[long],GALP[lat],
                        s=20,transform=data_crs,
                        edgecolors='k',linewidth=0.1
                        , marker='^'
                        )

        
    ax[0,1].set_title('Sensor type')


    #Depth of station zoomed into galap
    merm = ax[1,0].scatter(GALP[long],GALP[lat],
                        s=20,transform=data_crs,
                        c = GALP[depth], cmap='winter', norm= norm,
                        edgecolors='k',linewidth=0.2, marker='^')
    
    #Type zoomed into galap shows mermaid and normal
    ax[1,1].scatter(GALP[long],GALP[lat],
                        s=20,transform=data_crs,color='black', label='Other',
                        edgecolors='k',linewidth=0.2, marker='^')
    ax[1,1].scatter(mermaid_lon,mermaid_lat,
                        s=20,transform=data_crs,color='lightgreen', label ='mermaid',
                        edgecolors='k',linewidth=0.2, marker='v')
    ax[1,1].legend()
    
    # mermaid_loc = plt.scatter(mermaid_lon,mermaid_lat,
    #                     s=10,transform=data_crs,color='y')
    fig.colorbar(land_rloc,ax=ax[0,0],shrink=0.9,label='Depth (km)')
    fig.colorbar(merm,ax=ax[1,0],shrink=0.9,label='Depth (km)')

    
    for a in ax.flat:
        gl = a.gridlines(
        linewidth=0.5,
        draw_labels=True,
        color='gray',
        alpha=0.5,
        linestyle='--'
        )
        # Customize label appearance and visibility
        gl.inline_labels = True
        gl.x_inline = True
        gl.top_labels = False       # Turn off labels at the top
        gl.right_labels = False     # Turn off labels on the right
        gl.xlabel_style = {'size': 8, 'color': 'black'}
        gl.ylabel_style = {'size': 8, 'color': 'black'}
        gl.xlocator = mticker.MultipleLocator(2)
        gl.ylocator = mticker.MultipleLocator(2)


    plt.tight_layout()
    plt.show()
    
    # -----------------------------------------
    # The graphs are limited to reciever location initially
    
    return 

# %% reciever_loc_unid

'''
SUMMARY

Plot of unidentified mermaid locations when triggered from GPS,
Focused on Glap

Often used to get certain event location
'''

def reciever_loc_unid(unmer_df, title=None):
    
    fig, ax = plt.subplots(1,2,figsize=(10, 10),
                       subplot_kw={'projection': ccrs.Mollweide(central_longitude=180)})
        
    #Obtaining the transform coords
    data_crs = ccrs.PlateCarree()
    for a in ax.flat:
        a.coastlines(linewidth=0.3)
    

    ax[0].set_extent([-102, -80, -7.5, 5], crs=ccrs.PlateCarree()) # Limiting to Galap
    
    lonmin=unmer_df['stlo'].min()-0.1
    lonmax=unmer_df['stlo'].max()+0.1
    latmin=unmer_df['stla'].min()-0.1
    latmax=unmer_df['stla'].max()+0.1
    ax[1].set_extent([lonmin, lonmax,latmin , latmax], crs=ccrs.PlateCarree()) # Limiting to Galap

    stations = unmer_df['station'].unique()
    colours = plt.cm.tab20(np.linspace(0, 1, len(stations)))
    # Depth data
    for a in ax.flat:
        for station, colour in zip(stations, colours):
            land_rloc = a.scatter(
                unmer_df.loc[unmer_df['station']==station,['stlo']],
                unmer_df.loc[unmer_df['station']==station,['stla']],
                s=30,
                color=colour,
                edgecolors='k',
                linewidth=0.1,
                marker='^',
                transform=data_crs,
                label=f'Station {station}')
        n = unmer_df['network'].count()
    if title == None:    
        ax[1].set_title(f'Unidentified mermaid record trigger location with depth, N={n}')
    else:
        ax[1].set_title(f'{title}, N={n}')
    ax[1].legend()
   

    # mermaid_loc = plt.scatter(mermaid_lon,mermaid_lat,
    #                     s=10,transform=data_crs,color='y')

    for a in ax.flat:
        gl = a.gridlines(
        linewidth=0.5,
        draw_labels=True,
        color='gray',
        alpha=0.5,
        linestyle='--'
        )
        # Customize label appearance and visibility
        gl.inline_labels = True
        gl.top_labels = False       # Turn off labels at the top
        gl.right_labels = False     # Turn off labels on the right
        gl.xlabel_style = {'size': 8, 'color': 'black'}
        gl.ylabel_style = {'size': 8, 'color': 'black'}
        gl.xlocator = mticker.MultipleLocator(2)
        gl.ylocator = mticker.MultipleLocator(2)


    plt.tight_layout()
    plt.show()
    
    # -----------------------------------------
    # The graphs are limited to reciever location initially
    
    return 

# %% Location of all 

'''
SUMMARY
Plot of all mermaid trigger locations when triggered from GPS,
with symbol for mermaid and colour for day

Plot byt time period

Uses PlateCarree projection and Bathymtery data from 

Bathymotry data from
www.naturalearthdata.com/

INPUT: Mermaid dataframe hopefully made using MERMAID_DF
Can also accept a title string input

    outputs the plot
'''


def reciever_loc_all(mer_df, title=None,show=True):
    
    fig, ax = plt.subplots(1,1,figsize=(10, 10),
                       subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
        
    #Obtaining the transform coords
    data_crs = ccrs.PlateCarree()
    bath_leg = bathym(ax,leg_loc='lower left',ncol=2,fontsize=10,title_fontsize=12)

    ax.coastlines(linewidth=0.3)
    

    
    lonmin=mer_df['stlo'].min()-1
    lonmax=mer_df['stlo'].max()+1
    latmin=mer_df['stla'].min()-1
    latmax=mer_df['stla'].max()+1

    ax.set_extent([lonmin, lonmax,latmin , latmax], crs=ccrs.PlateCarree()) # Limiting to Galap

    stations = mer_df['station'].unique()
    dates = sorted(mer_df['date'].unique())
    markers = ['o', '^', 's', 'D', '*', 'P', 'X', 'v', 'p']
    
    date_colours = plt.cm.cividis(np.linspace(0, 1, len(mer_df['date'].unique())))
    date_colour_map = dict(zip(dates, date_colours))
    # Depth data
    for i,station in enumerate(stations):
    #for station, colour,i in zip(stations, date_colours, range(len(stations))):
        sub_station = mer_df[mer_df['station'] == station]
        point_colours = sub_station['date'].map(date_colour_map) # making a color map for each day
    
        ax.scatter(
            sub_station['stlo'],
            sub_station['stla'],
            s=50,
            color=list(point_colours),
            edgecolors='k',
            linewidth=0.4,
            marker=markers[i],
            transform=data_crs,
            zorder=5
            )
    n = mer_df['network'].count()
    if title == None:    
        ax.set_title(f'Mermaid trigger location, N={n}')
    else:
        ax.set_title(f'{title}, N={n}')
    # --- Legend 1: marker == station ---
    marker_handles = [
        Line2D([0], [0], marker=markers[i], color='grey', linestyle='None',
               markeredgecolor='k', markersize=8, label=str(station))
        for i, station in enumerate(stations)
    ]
    legend1 = ax.legend(handles=marker_handles, title='Station',
                         loc='upper left', bbox_to_anchor=(1.02, 1))
    ax.add_artist(legend1)  # keep it alive
    
    ax.add_artist(bath_leg)
    #--- Legend 2: colour == date ---
    date_handles = [
        Line2D([0], [0], marker='o', color=date_colour_map[d], linestyle='None',
               markersize=8, label=str(d))
        for d in dates
    ]
    legend2 = ax.legend(handles=date_handles, title='Date',
                         loc='upper left', bbox_to_anchor=(1.02, 0.5))
    

    # mermaid_loc = plt.scatter(mermaid_lon,mermaid_lat,
    #                     s=10,transform=data_crs,color='y')

    gl = ax.gridlines(
    linewidth=0.5,
    draw_labels=True,
    color='gray',
    alpha=0.5,
    linestyle='--'
    )
    # Customize label appearance and visibility
    gl.inline_labels = True
    gl.top_labels = False       # Turn off labels at the top
    gl.right_labels = False     # Turn off labels on the right
    gl.xlabel_style = {'size': 8, 'color': 'black'}
    gl.ylabel_style = {'size': 8, 'color': 'black'}
    gl.xlocator = mticker.MultipleLocator(2)
    gl.ylocator = mticker.MultipleLocator(2)


    plt.tight_layout()
    if show==True:
        plt.show()
    
    # -----------------------------------------
    # The graphs are limited to reciever location initially
    
    return fig


# %%
import matplotlib.ticker as mticker

def reciever_loc_all_data(mer_df, title=None, max_freq=10, min_freq = 5,show=True,s=0):
    '''
    Plots mermaid trigger location giving day a colour, mermaid a symbol and size according to data 
    
    Need to add date to each 
    '''
    fig, ax = plt.subplots(1,1,figsize=(10, 10),
                       subplot_kw={'projection': ccrs.PlateCarree(central_longitude=180)})
        
    #Obtaining the transform coords
    data_crs = ccrs.PlateCarree()
    bath_leg = bathym(ax,ncol=2,fontsize=10,title_fontsize=12)

    ax.coastlines(linewidth=0.3)
    

    
    lonmin=mer_df['stlo'].min()-1
    lonmax=mer_df['stlo'].max()+1
    latmin=mer_df['stla'].min()-1
    latmax=mer_df['stla'].max()+1

    ax.set_extent([lonmin, lonmax,latmin , latmax], crs=ccrs.PlateCarree()) # Limiting to Galap

    stations = mer_df['station'].unique()
    markers = ['^', 's', 'D', '*', 'P', 'X', 'v', 'p','o', ]
    
    vmin = min(mer_df['max_amplitude'])
    vmax = max(mer_df['max_amplitude'])
    # Depth data
    for i,station in enumerate(stations):
    #for station, colour,i in zip(stations, date_colours, range(len(stations))):
        sub_station = mer_df[mer_df['station'] == station]
        
        #New scatter for each station
        sc = ax.scatter(
            sub_station['stlo'],
            sub_station['stla'],
            s=60,
            c=sub_station['max_amplitude'],
            vmin=vmin,
            vmax=vmax,
            cmap="plasma",
            edgecolors='k',
            linewidth=0.4,
            marker=markers[i],
            transform=data_crs,
            zorder=5
            )

    
    n = mer_df['network'].count()
    
    if title == None:    
        ax.set_title(f'Mermaid trigger location with rumblings depth, N={n}')
    else:
        ax.set_title(f'{title}, N={n}')
    # --- Legend 1: marker == station ---
    marker_handles = [
        Line2D([0], [0], marker=markers[i], color='grey', linestyle='None',
               markeredgecolor='k', markersize=8, label=str(station))
        for i, station in enumerate(stations)
    ]
    legend1 = ax.legend(handles=marker_handles, title='Station',
                         loc='upper right')
    ax.add_artist(legend1)  # keep it alive
    
    ax.add_artist(bath_leg)
    
    cax = fig.add_axes([0.20, 0.15, 0.60, 0.03])
    fig.colorbar(sc, cax=cax, orientation='horizontal',
                        label=f'Max amplitude Counts between {min_freq}-{max_freq} hz'
                        )





    # mermaid_loc = plt.scatter(mermaid_lon,mermaid_lat,
    #                     s=10,transform=data_crs,color='y')

    gl = ax.gridlines(
    linewidth=0.5,
    draw_labels=True,
    color='gray',
    alpha=0.5,
    linestyle='--'
    )
    # Customize label appearance and visibility
    gl.inline_labels = True
    gl.top_labels = False       # Turn off labels at the top
    gl.right_labels = False     # Turn off labels on the right
    gl.xlabel_style = {'size': 8, 'color': 'black'}
    gl.ylabel_style = {'size': 8, 'color': 'black'}
    gl.xlocator = mticker.MultipleLocator(2)
    gl.ylocator = mticker.MultipleLocator(2)

    if show ==True:
        plt.show()
    
    # -----------------------------------------
    # The graphs are limited to reciever location initially
    
    return ax, fig

# %%

   
'''
Creates a graph containign all mermaid eq magnitude total and individually
In a bargraph
'''
def data_plots(df,dtype,data,bins, unit=None,drange=(4,8.5)):
    '''
    Makes plot of all mermaid data
    Default is for magnitude
    dtype ie magnitude or gcarc == str
    data == name of pandas array value
    
    also plots mean value 
    '''
    
    # Edit this to change graph colour
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
    fig,ax = plt.subplots(2,5,figsize=(40,10))
    ax=ax.flatten()
    
    #final plot of all
    ax[0].hist(df[data],bins=bins,
               linewidth=1,
               edgecolor='black',
               color='red',
               range=drange
               ) 
    if dtype =='gcarc':    
        dtype = 'Epicentral distance'
        ax[0].set_title(f'{dtype} of earthquake recordings by all mermaid')
     
    else:
        ax[0].set_title(f'{dtype} of earthquake recordings by all mermaid')
        ax[0].axvline(x=df[data].mean(), linestyle='--',color='grey')
    ax[0].set_xlabel(dtype)

    #Months alive
    t1= df['starttime'].min()
    t2= df['starttime'].max()
    months = (t2.year - t1.year) * 12 + (t2.month - t1.month)
    events=df['evlo'].count()
    ax[0].text(
        0.70, 0.90,
        f'Event N = {events}\nmission length = {months}',
        transform=ax[0].transAxes
        )
    
    for i,sensor in enumerate(df['station'].unique()):
    #enumerate ensure i can also get the index
        i=i+1 #as first is total 
        df_data= df.loc[df['station']==sensor,[data]]
        ax[i].hist(df_data,bins=bins,
                   linewidth=1,
                   edgecolor='black',
                   color=colours[i-1],
                   range=drange
                   )
        ax[i].set_title(f'Mermaid {sensor}')
        ax[i].set_xlabel(dtype)
        
        #Months alive
        t1= df.loc[df['station']==sensor,['starttime']].min().item()
        t2= df.loc[df['station']==sensor,['starttime']].max().item()
        
        
        months = (t2.year - t1.year) * 12 + (t2.month - t1.month)
        ax[i].text(
            0.75, 0.90,
            f'Event N = {len(df_data)}\nmonths alive = {months}',
            transform=ax[i].transAxes
            )
        
        #setting unit
        if unit != None:
            ticks = np.arange(0, 181, 60)
            ax[i].set_xticks(ticks,[f'{t:.1f}{unit}' for t in ticks])
        
        else:
            ax[i].set_ylim(0,20)
            ax[i].axvline(x=df_data[data].mean(), linestyle='--',color='grey')

        print(i)
        
    ax[0].set_ylabel('counts')
    ax[5].set_ylabel('counts')
    
    
    
    plt.show()
    

# %% data plots for unidentified by type

def data_plots_un_type(df,df2,df3,types=['type1','type2','type3']):
    '''
    Makes plot of all unidentified mermaid data statistics

    df is an array plotted bt pandas
    
    Has option of only station type  wich included the colours or 
    
    optiosn to put in multiple df to make a stacked
    '''
    # data_plots_un_amount(mer_df)
    
    st = read('data/galapagos/mermaid*/*identified/sac/m*.*.sac')

    #calculating months alive each
    entire_df = mermaid_df(st)
    months=[]
    for sensor in (entire_df['station'].unique()):
        t1= entire_df.loc[entire_df['station']==sensor,['starttime']].min().item()
        t2= entire_df.loc[entire_df['station']==sensor,['starttime']].max().item()
        
        months.append((t2.year - t1.year) * 12 + (t2.month - t1.month))

    st = read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')
    mer_df = mermaid_df(st)
    total=len(mer_df['station'])
    
    fig,ax = plt.subplots(1,1,figsize=(10,8))

    dfs = [df, df2, df3]
    type_labels = types  # adjust to your actual categories
    colours = ['#4292c6', '#009E73', '#E69F00']    # one colour per dataframe
    
    # get the full set of stations across all three dataframes, sorted consistently
    all_stations = sorted(set().union(*[d['station'].unique() for d in dfs]))
    
    # build "months alive" labels using the first dataframe that has that station
    labels = []
    
    for i,s in enumerate(entire_df['station'].unique()):
        labels.append(f'MERMAID {s}\nmonths alive ={months[i]}')
             
    
    x = np.arange(len(all_stations))
    bottom = np.zeros(len(all_stations))
    
    for mer_df, colour, type_label in zip(dfs, colours, type_labels):
        counts = mer_df['station'].value_counts().reindex(all_stations, fill_value=0)
        ax.bar(x, counts.values, bottom=bottom, color=colour,
               edgecolor='k', linewidth=0.2, label=f'{type_label}, Total={len(mer_df)}')
        bottom += counts.values
    
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.legend()

    t1= entire_df['starttime'].min()
    t2= entire_df['starttime'].max()
    
    months = ((t2.year - t1.year) * 12 + (t2.month - t1.month))

    
    ax.set_title(f'No of triggers that contain the belllow 3 catagories in Mermaid uncatagorised record \n total triggers = {total}  | total mission length = {months} months')
    
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylabel('Number of triggers unidentified')

    return fig,ax

# %% Seismograms with guust plots on 
from obspy.taup import TauPyModel

def singleplot_filt_picks(st,st_filt,picks,filt_type, axs=1, fig=1,freq_max = 0,
                             freq_min= 1, freq= 0, show = True,title=True,
                             arrivals=['ttbasic']
                             ):
    '''
    arrivals: gives the obspy.arrival output giving the entire list of arrivals 
    first_arrivals: the brackdown of obpy arrivals and only gives the first of each type
    
    You can use axs to plot where you like the 2
    
    For non bandpass use just freq
    Ive change this function to move the title in relation to plot filtered
    
    
    Similar warining about tau P PARAMETERS
    ALSO ONLY PLOTS FIRST OF A TYPE OF ARRIVAL TO PREVENT CLUTTER
    '''
    mer_picks = picks[picks['netw']=='MERMAID']
    
    tr = st[0]
    
    ##############################################
    # Tau p part
    model = TauPyModel(model = 'ak135')
    arrivals= model.get_travel_times (source_depth_in_km = tr.stats.sac.evdp,
                                      distance_in_degree = tr.stats.sac.gcarc,
                                      phase_list=arrivals,
                                      receiver_depth_in_km=1.5) #see deep wiki doc for exact phases
                                        #estimating arrival times for that trace
    #Keeping the earliest arrivals of each phase splitting the two
    first_arrivals = {}

    for arrival in arrivals:
        if arrival.name not in first_arrivals:
            first_arrivals[arrival.name] = arrival
                             
    first_arrivals = list(first_arrivals.values())

    if axs==1:
        fig, axs = plt.subplots(1, 2, figsize=(30, 5))
    
    #####################################################    
    t = tr.times()  # Time in seconds relative to trace start
    ax=axs[0]
    ax.plot(t, tr.data, color='red')
    ax.grid()
    ax.set_title('Raw')
    ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    ax.set_ylabel('Counts')
    
    tr = st_filt[0]
    ax=axs[1]
    t = tr.times()  # Time in seconds relative to trace start
    ax.plot(t, tr.data)
    ax.grid()
    ax.set_title('Filtered')
    ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    
    ##################################################
    #plotting arivals on
 
    phase_names = []
    for i in range(len(first_arrivals)):
        t = first_arrivals[i].time
        t = t + tr.stats.sac.o
        # correction for being 1.5km bellow sea of 0.7 given 1s if entire water and 0.27 quicker if solid
        t = t+1
        length_t=tr.stats.npts/20
        if t> length_t:
            break # so later arrivals not shown
        elif t<0:
            # so not regestered diffracted arrivals not shown
            continue
        else:
            axs[0].axvline(x=t, linestyle='--',color='black')
            axs[1].axvline(x=t, linestyle='--',color='black')

            phase_names.append(first_arrivals[i].name)
            
    ax.annotate(phase_names,xy=(0, 1),xycoords='axes fraction',ha='left',va='top',fontsize=20)

    
    ################################################
    #Creating a title between each row
    fe = FlinnEngdahl()
    # Making 2 sets incase filter has max and min or not
    if title==True:
        if filt_type == 'bandpass':
            region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)
            y = axs[0].get_position().y1 +0.01 # just above row
            fig.text(
                0.5,
                y,
                f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | region= {region} |Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km |\n Dist = {tr.stats.sac.gcarc:.1f} | Demean + Detrend + taper |filtering method= {filt_type} | freq = {freq_min:.1f}-{freq_max:.1f} Hz ',
                ha='center', # Need to include distance 
                fontsize=15
            )
        else:
           
            region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)
    
            y = axs[0].get_position().y1 +0.01 # just above row
            fig.text(
                0.5,
                y,
                f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | region= {region} | Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km |\n Dist = {tr.stats.sac.gcarc:.1f} | Demean + Detrend + taper | filtering method= {filt_type} | Freq = {freq:.1f} hz',
                ha='center', # Need to include distance 
                fontsize=15
            )
    else:
        #only works with bandpass
        region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)

        y = axs[1].get_position().y1 +0.01 # just above row
        fig.text(
            0.5,
            y,
            f'Demean + Detrend + taper |filtering method= {filt_type} | freq = {freq_min:.1f}-{freq_max:.1f} Hz',
             ha='center', # Need to include distance 
            fontsize=15
        )
    
    if show == True:
        plt.show()
    return arrivals,first_arrivals

# %% outputs numer of mermaids that triggered around the same time with a 2 hour buffer

def events_seen(mer_df, timeframe=(20*60)):
    '''
    INPUT: Has to be a pandas dataframe preferably make with MERMAID_DF 

    outputs numer of mermaids that triggered around the same time with a set timeframe 
    
    done by adding a extra date (just date not date time) column 
    Then adds a another colume with the avsolute datatime since 1 event to see the time around

    Also done to unique statiosn this doesnt concider the same station being triggered multiple times (removes lots of glitches
    
    Made by creatung a true or false mask
    
    OUTPUT
    A dataframe containing the start and entime of multitrigger period 
    Counts 
    Which stations

    '''
    mer_df['date'] = mer_df['starttime'].apply(lambda x: x.date())
    
    
    results = []
    
    
    mer_df['timestamp'] = mer_df['starttime'].apply(
        lambda x: UTCDateTime(x).timestamp
    )
    # Sort by timestamp
    mer_df = mer_df.sort_values('timestamp').reset_index(drop=True)
    
    #Finds if the time difference is within timeframe and on a different station
    mask = (
        (
            (mer_df['timestamp'].diff() <= timeframe) &
            (mer_df['station'] != mer_df['station'].shift())
        )
        |
        (
            (mer_df['timestamp'].diff(-1).abs() <= timeframe) &
            (mer_df['station'] != mer_df['station'].shift(-1))
        )
    )
    
    within_min = mer_df[mask].copy()
    
    
    # Create a new group whenever the gap exceeds set timeframe in seconds
    within_min['group'] = (
        within_min['timestamp'].diff().fillna(np.inf) > timeframe
        ).cumsum()
    
    counts = within_min.groupby('group').size()

    for group, count in counts.items():
        if count > 1:
            group_df = within_min[within_min['group'] == group]
            
            results.append({
                'start_time': group_df['starttime'].min(),
                'end_time': group_df['endtime'].max(),
                'count': count,
                'stations': list(group_df['station'])
                })
    
    results_df = pd.DataFrame(results)
    
    #Prints the amount of unique identifiecations per day
    print(results_df.to_string(index=False))
    
    return results_df

# %% Making datafram from mermaid data
# both identified an dnon
'''
SUMMARY

Takes a obspy stream data in SAC format and converts it into a easier to use (for me) pandas dataframe 
Will work if catagories dont exist will just be empty 

Criterion: the SIgnal to noise ratio that had to be exceeded to trigger
o - The time delay between event and start of trigger 
'''
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
            "o": tr.stats.sac.get("o"),
            "stla": tr.stats.sac.get("stla"),
            "stlo": tr.stats.sac.get("stlo"),
            "stdp": tr.stats.sac.get("stdp"),
            "evla": tr.stats.sac.get("evla"),
            "evlo": tr.stats.sac.get("evlo"),
            "gcarc": tr.stats.sac.get("gcarc"),
            "evdp": tr.stats.sac.get("evdp"),
            "mag": tr.stats.sac.get("mag"),
            'SNR (USER0)': tr.stats.sac.get('user0'),
            'CRITERION (USER1)': tr.stats.sac.get('user1'),

        })

    mer_df = pd.DataFrame(mer_record)
    
    return mer_df

# %% Ploting spec

from obspy import Stream
from my_code.mer_plot_f import spectrogram_plot, spectrogram_plot_uni
from my_code.commands.import_iris_data import iris_import

#Filtering by starttime
def plot_save_spec(st,startdate,enddate):
    
    '''
    Contains the changable parameters for creating a specogram and 3 seismograms bellow
    seismograms are Raw, first filtered, second filtered [optional]
    
    Plots phase arrivals if identified
    
    IMPORTANT DEFAULTS have to be changed in this code
    - Uses a 0.25 Tukey filtered (cosine but less)
    - ttbasic in tauP arrivals 
    - Filtering is a 1 pass causal
    - Path it saves to is hardcoded for me so change 
    - Window length for spec is set to data length/ sampler ate
    
    '''
    st = Stream(
        tr for tr in st
        if UTCDateTime(tr.stats.starttime) >= UTCDateTime(startdate) 
        and UTCDateTime(tr.stats.endtime) <= UTCDateTime(enddate) 
        # and tr.stats.station in stations
        )
    land= input('Add the Galpagos land station PAYG [y/n]') or 'n'

    if land=='y' or land=='Y':
        st = iris_import(st,length='individual')
    
    while True:
        if_log = input('linear or log scale spectrogram :') or 'linear'
        if if_log =='linear':
            log= False
            break
        elif if_log == 'log':
            log = True
            break
        else:
            print('Invalid option')
    
    spec_freq_maximum = float(input('Spectrogram max frequency (hz) [default 5]: ') or 5)
    spec_freq_minimum = float(input('Spectrogram min frequency (hz) [default 0.1]: ') or 0.1)
    
    if (input('Change other options (y/n)? ') or 'n') == 'n':
        freq_maximum= 2.5
        freq_minimum=0.5
        freq_max2 = 10
        freq_min2 = 2.5
    
        taper = ('tukey',0.25)
        phase_arrival = ['ttbasic']
    else:
        freq_maximum=float(input('Filtered seismogram max freqency [default 2.5]: ') or 2.5)
        freq_minimum=float(input('Filtered seismogram min freqency [default 0.5]: ') or 0.5)
        freq_max2 = float(input('Second filtered seismogram max freqency [default 0 not exist]: ') or 0)
        freq_min2 = float(input('Second filtered seismogram min freqency [default 0 not exist]: ') or 0)
        taper = ('tukey',0.25)
        phase_arrival = 'ttbasic'
    
    
    for i in range(len(st)):
        t= UTCDateTime(st[i].stats.starttime)
        time= t.strftime("%Y%m%dT%H%M%S")
        station=st[i].stats.station
        #Hardcoded path should be changed 
        png_file = Path(f'/home/gregory/Documents/mermaid_glap/Plots/spectrograms/temp/{time}.m{station}.png')
        
        if png_file.exists():
            continue
        else:
            pass
        nfft = int(len(st[i].data)/st[i].stats.sampling_rate)
        
        if st[i].stats.sac.get("evlo") is None or st[i].stats.sac.get("evlo")== 0:
            fig = spectrogram_plot_uni(
                st[i:i+1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
                spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
                nfft=nfft,
                log=log,
                taper=taper
                )
        
        else:
            fig,arrivals = spectrogram_plot(
                st[i:i+1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
                spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
                arrivals=phase_arrival,
                nfft=nfft,
                log=log,
                taper=taper
                )
            


        png_file = Path(f'/home/gregory/Documents/mermaid_glap/Plots/spectrograms/temp/{time}.m{station}.png')
        
        fig.savefig(png_file, dpi=200, bbox_inches='tight')
        plt.close(fig)
            
        
    return

# %% TAKES A INPUT START AND END DATE PLOTS LOCATION AND SAVES SPECTRA



def loc_spectro(st,startdate,enddate):
    
    '''
    Takes in a uct dattime
    '''
    starttime=startdate
    endtime=enddate
    # starttime = datetime.strptime(startdate, "%Y%m%d").strftime("%Y-%m-%d")
    # endtime = datetime.strptime(enddate, "%Y%m%d").strftime("%Y-%m-%d")
    
    out_dir = Path("Plots/spectrograms/multi_trig")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    
    # Reading in both identified and non also speed up using this slighly
    
    mer_df = mermaid_df(st)
    
        
    
    mer_df['date'] = mer_df['starttime'].apply(lambda x: x.date())
        

    #plotting specta
    freq_maximum=2
    freq_minimum=0.5
    spec_freq_maximum = 5
    spec_freq_minimum = 0.1
    freq_max2 = 10
    freq_min2 = 2.5
    
    # making strea within time
    st = Stream(
        tr for tr in st
        if UTCDateTime(tr.stats.starttime) >= UTCDateTime(starttime) 
        and UTCDateTime(tr.stats.endtime) <= UTCDateTime(endtime) 
        # and tr.stats.station in stations
        )
    
    # arrivals_list=['PKP','PKIKP','pPKIKP']
    for i in range(len(st)):
        
        t= UTCDateTime(st[i].stats.starttime)
        time= t.strftime("%Y%m%dT%H%M%S")
        station=st[i].stats.station
        filepath = f'{out_dir}/5T.{time}.m{station}.png'

        if os.path.exists(filepath):
            print('yes')
            continue           
            
        nfft = int(len(st[i].data)/20)

        fig= spectrogram_plot_uni(
            st[i:i+1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
            spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
            nfft=nfft,
            log=False,
            taper=('tukey',0.25)
            )
        
        plt.show()

        # Remember ti change save location
        fig.savefig(f'{out_dir}/5T.{time}.m{station}.png', dpi=100, bbox_inches='tight')
        

