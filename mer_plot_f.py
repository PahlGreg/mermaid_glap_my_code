#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 15:39:50 2026

@author: gregory

Functions list:
    
"""

import obspy
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from obspy.geodetics import FlinnEngdahl #for getting quake location
from obspy.core import UTCDateTime
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cartopy.io.shapereader as shpreader
from obspy.geodetics import FlinnEngdahl
import obspy.signal
from matplotlib.ticker import MultipleLocator
import matplotlib.ticker as mticker
from obspy.taup import TauPyModel

# %% Plot a single seismogram

def single_plot(st):
    """
    Plots a sing raw seismograms frp, a stream
    This code doesnt have as update titles as only used for a single look
    """
    
    tr = st[0]
    fig, ax = plt.subplots(figsize=(15, 5))
    ax.plot(tr.times(), tr.data, "b-")
    fig.autofmt_xdate()
    ax.set_xlabel(f'Time (s)')
    ax.set_ylabel(f'counts')
    ax.grid()

    plt.annotate(f'{tr.get_id}',xy=(0,0),xycoords='axes points')
    plt.show()
# %% Single plot of raw and filtered seismogram

def singleplot_filt(st,st_filt,filt_type, axs=1, fig=1,freq_max = 0, freq_min= 1, freq= 0, show = True,title=True):
    """
    Plots a single entry stream object and the filtered version next to it
    Remember this filter is a single pass so causality mainatined (i think)

    Parameters
    ----------
    st : TYPE
        a single stream object else will only take first one.
    st_filt : TYPE
        The steam but has had basic_filt function applied that de mean and de trends plus apply a cosine taper to smooth edge .
    filt_type : 
        string bandpass or not

    axs : so you can chose where to plot not just next to each other but defult is next, use matplotlib axis system
    
    title:
        Doesnt remove the title keeps the filtering parameters but not event info attached
        Only works for bandpass
    Returns
    -------
    None
    """

    
    #Can also chose to add a line for first arrival
    if axs==1:
        fig, axs = plt.subplots(1, 2, figsize=(30, 5))
    
    tr = st[0]
    
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

        y = axs[0].get_position().y1 +0.01 # just above row
        fig.text(
            0.5,
            y,
            f'Demean + Detrend + taper |filtering method= {filt_type} | freq = {freq_min:.1f}-{freq_max:.1f} Hz',
             ha='center', # Need to include distance 
            fontsize=15
        )
    if show == True:    
        plt.show() # for if you do multiple single or use in other functions
# %% Mulotiple bandpasses single plot
    
def singleplot_filt_multiband(st,st_filt1,st_filt2, axs=1, fig=1,freq_max1 = 5,
                             freq_min1= 2,freq_max2 = 2, freq_min2= 0.5,
                             show = True,title=True,
                             ):
    '''
    only works for unidentified
    Plots 2 different bandpass filters
    
    You can use axs to plot where you like the 2
    
    For non bandpass use just freq
    Ive change this function to move the title in relation to plot filtered
    
    
    '''

    tr = st[0]
    

    if axs==1:
        fig, axs = plt.subplots(1, 3, figsize=(30, 5))
    
    #####################################################    
    t = tr.times()  # Time in seconds relative to trace start
    ax=axs[0]
    ax.plot(t, tr.data, color='red')
    ax.grid()
    ax.set_title('Raw')
    ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    ax.set_ylabel('Counts')
    
    tr = st_filt1[0]
    ax=axs[1]
    t = tr.times()  # Time in seconds relative to trace start
    ax.plot(t, tr.data)
    ax.grid()
    ax.set_title('Filtered')
    ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    
    tr = st_filt2[0]
    ax=axs[2]
    t = tr.times()  # Time in seconds relative to trace start
    ax.plot(t, tr.data)
    ax.grid()
    ax.set_title('Filtered')
    ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    
    
    ################################################
    #Creating a title between each row
    # Making 2 sets incase filter has max and min or not
    if title==True:
      
        y = axs[0].get_position().y1 +0.01 # just above row
        fig.text(
            0.5,
            y,
            f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | SNR={tr.stats.sac.user0} |\n  Demean + Detrend + taper |filtering method= bandpass | freq upper = {freq_min1:.1f}-{freq_max1:.1f} Hz | freq lower = {freq_min2:.1f}-{freq_max2:.1f} Hz',
            ha='center', # Need to include distance 
            fontsize=15
        )
     
    else:

        y = axs[1].get_position().y1 +0.01 # just above row
        fig.text(
            0.5,
            y,
            f'Demean + Detrend + taper |filtering method= bandpass | freq = {freq_min1:.1f}-{freq_max1:.1f} Hz',
             ha='center', # Need to include distance 
            fontsize=15
        )
        y = axs[2].get_position().y1 +0.01 # just above row
        fig.text(
            0.5,
            y,
            f'Demean + Detrend + taper |filtering method= bandpass | freq = {freq_min2:.1f}-{freq_max2:.1f} Hz',
             ha='center', # Need to include distance 
            fontsize=15
        )
    axs[2].xaxis.set_minor_locator(MultipleLocator(5))

    if show == True:
        plt.show()
    return 

# %% Plot of multiple seismograms raw and filtered usign a highpass or bandpass



def multiplot_filt(st,st_filt,filt_type,freq_max = 0, freq_min= 1, freq= 0,sharey=False, info=True):
    
    '''
    Same as single but can be done for a single long stream,
    Also no option for editing plot location 
    Does automatically detect if unidentified and changes title accordingly
    
    Remember there has been some changes to simple plot that should be brough tot multi

    Also REMEMBER DEFAULT ASSUMTIONS WHEN FILTERING
    
    Adds info which if it doesnt exist only plots date and mermad
    '''
    
    fig, axs = plt.subplots(len(st), 2, figsize=(30, 5*len(st)))
    fig.subplots_adjust(hspace=0.5)
    
    for ax, tr in zip(axs[:,0], st):
        t = tr.times()  # Time in seconds relative to trace start
        ax.plot(t, tr.data, color='red')
        ax.grid()
        ax.set_title('Raw')
        ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
        ax.set_ylabel('Counts')
    
    for ax, tr in zip(axs[:,1], st_filt):
        t = tr.times()  # Time in seconds relative to trace start
        ax.plot(t, tr.data)
        ax.grid()
        ax.set_title('Filtered')
        ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
        
    if sharey==True:
        col_axes = axs[:, 1]          # all rows, column 1
        for ax in col_axes[1:]:
            ax.sharey(col_axes[0]) 
    #Creating a title between each row
    fe = FlinnEngdahl()
    # Making 2 sets incase filter has max and min or not
    ## Seperates unidentified and identified cuz titles different 

        
    if not hasattr(tr.stats, "sac") or tr.stats.sac.evla==0:
        if filt_type == 'bandpass':
            for i, tr in enumerate(st):
                if info:
                    text=f'Unidentified | Date={str(tr.stats.starttime)[:13]} | station={tr.stats.station} | station depth= {tr.stats.sac.stdp:.0f} | SNR= {tr.stats.sac.user0:.3f} '
                else:
                    text=f'Unidentified | Date={str(tr.stats.starttime)[:13]} | station={tr.stats.station}'
                #title breaks when length is too long due to changing size simple alter position
                offset_pts = 20  # desired gap above axes
                offset_fig = offset_pts / (72 * fig.get_figheight())
                i 
                y = axs[i, 0].get_position().y1 + offset_fig
                
                fig.text(
                    0.5,
                    y,
                    f'{text} | Demean + Detrend + taper | Filtering method= {filt_type} | Freq = {freq_min:.1f}-{freq_max:.1f} Hz ',
                    ha='center',
                    va='bottom',
                    fontsize=15
                )
        else:
            for i, tr in enumerate(st):
                if info:
                    text=f'Unidentified | Date={str(tr.stats.starttime)[:13]} | station={tr.stats.station} | station depth= {tr.stats.sac.stdp:.0f} | SNR= {tr.stats.sac.user0:.3f} '
                else:
                    text=f'Unidentified | Date={str(tr.stats.starttime)[:13]} | station={tr.stats.station}'
                offset_pts = 20  # desired gap above axes
                offset_fig = offset_pts / (72 * fig.get_figheight())
               
                y = axs[i, 0].get_position().y1 + offset_fig
               
                fig.text(
                    0.5,
                    y,
                    f'{text} | Demean + Detrend + taper | Filtering method= {filt_type} | Freq = {freq_min:.1f}-{freq_max:.1f} Hz ',
                    ha='center',
                    fontsize=15
                )
    else:
        if filt_type == 'bandpass':
            for i, tr in enumerate(st):
                region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)
    
                offset_pts = 20  # desired gap above axes
                offset_fig = offset_pts / (72 * fig.get_figheight())
                
                y = axs[i, 0].get_position().y1 + offset_fig
                fig.text(
                    0.5,
                    y,
                    f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | station depth= {tr.stats.sac.stdp:.0f} | region= {region} | Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km |\n Dist = {tr.stats.sac.gcarc:.1f} | SNR= {tr.stats.sac.user0:.3f} | Demean + Detrend + taper | Filtering method= {filt_type} | Freq = {freq_min:.1f}-{freq_max:.1f} Hz',
                    ha='center', 
                    fontsize=15
                )
        else:
            for i, tr in enumerate(st):
                region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)
        
                offset_pts = 20  # desired gap above axes
                offset_fig = offset_pts / (72 * fig.get_figheight())
               
                y = axs[i, 0].get_position().y1 + offset_fig
                fig.text(
                    0.5,
                    y,
                    f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | station depth= {tr.stats.sac.stdp:.0f} | region= {region} | Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km |\n Dist = {tr.stats.sac.gcarc:.1f} | SNR= {tr.stats.sac.user0:.3f} | Demean + Detrend + taper | filtering method= {filt_type} | Freq = {freq:.1f} hz',
                    ha='center', # Need to include distance 
                    fontsize=15
                )
    


    return fig, axs
# %% Basic processing


def basic_proc(st,max_percentage=0.03,taper_type='cosine'):
    #De trends, demenas and tapers 
    # Done before every filter plot 
    st.detrend('linear')
    st.detrend('demean')
    st.taper(max_percentage=0.03,type=taper_type, max_length=5)
    
    return st

# %% Calculating taup arrivals for that trace

def taup_arrivals(tr,arrivals=['ttbasic'],model='ak135'): #mayble add some parameteers i can change

    '''
    
    arrivals: gives the obspy.arrival output giving the entire list of arrivals 
    first_arrivals: the brackdown of obpy arrivals and only gives the first of each type
    
    Warning of the parameters selected
    '''
    if not isinstance(tr,obspy.Trace):
        raise TypeError(
            f'Expected obspy.trace, got {type(tr._name_)}'
        )
        
    model = TauPyModel(model =model)
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
    
    return arrivals, first_arrivals

# %% 

'''
RETREVE BANDPASS assesing code  FROM BACKUPjmm
'''


# %% Single plot of the arrivals (from tau P)



def singleplot_filt_arrivals(st,st_filt,filt_type, axs=1, fig=1,freq_max = 0,
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
        fig, axs = plt.subplots(2, 1, figsize=(15, 10))
    
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

# %% Single plot multi bandpasses with arrivals

def singleplot_filt_arrivals_multiband(st,st_filt1,st_filt2, axs=1, fig=1,freq_max1 = 5,
                             freq_min1= 2,freq_max2 = 2, freq_min2= 0.5,
                             show = True,title=True,
                             arrivals=['ttbasic']
                             ):
    '''
    arrivals: gives the obspy.arrival output giving the entire list of arrivals 
    first_arrivals: the brackdown of obpy arrivals and only gives the first of each type
    Plots 2 different bandpass filters
    
    You can use axs to plot where you like the 2
    
    For non bandpass use just freq
    Ive change this function to move the title in relation to plot filtered
    
    
    Similar warining about tau P PARAMETERS
    ALSO ONLY PLOTS FIRST OF A TYPE OF ARRIVAL TO PREVENT CLUTTER
    '''

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
        fig, axs = plt.subplots(1, 3, figsize=(30, 5))
    
    #####################################################    
    t = tr.times()  # Time in seconds relative to trace start
    ax=axs[0]
    ax.plot(t, tr.data, color='red')
    ax.grid()
    ax.set_title('Raw')
    ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    ax.set_ylabel('Counts')
    
    tr = st_filt1[0]
    ax=axs[1]
    t = tr.times()  # Time in seconds relative to trace start
    ax.plot(t, tr.data)
    ax.grid()
    ax.set_title('Filtered')
    ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    
    tr = st_filt2[0]
    ax=axs[2]
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
            axs[2].axvline(x=t, linestyle='--',color='black')


            phase_names.append(first_arrivals[i].name)
            
    ax.annotate(phase_names,xy=(0, 1),xycoords='axes fraction',ha='left',va='top',fontsize=20)

    
    ################################################
    #Creating a title between each row
    fe = FlinnEngdahl()
    # Making 2 sets incase filter has max and min or not
    if title==True:
      
        region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)
        y = axs[0].get_position().y1 +0.01 # just above row
        fig.text(
            0.5,
            y,
            f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | region= {region} |Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km |\n Dist = {tr.stats.sac.gcarc:.1f} | Demean + Detrend + taper |filtering method= bandpass | freq upper = {freq_min1:.1f}-{freq_max1:.1f} Hz | freq lower = {freq_min2:.1f}-{freq_max2:.1f} Hz',
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
            f'Demean + Detrend + taper |filtering method= bandpass | freq = {freq_min1:.1f}-{freq_max1:.1f} Hz',
             ha='center', # Need to include distance 
            fontsize=15
        )
        y = axs[2].get_position().y1 +0.01 # just above row
        fig.text(
            0.5,
            y,
            f'Demean + Detrend + taper |filtering method= bandpass | freq = {freq_min2:.1f}-{freq_max2:.1f} Hz',
             ha='center', # Need to include distance 
            fontsize=15
        )
    axs[2].xaxis.set_minor_locator(MultipleLocator(5))
    if show == True:
        plt.show()
    return arrivals,first_arrivals

# %% Multiplot of tauP arrivals

def multiplot_filt_arrivals(st,st_filt,filt_type,freq_max = 0, freq_min= 1, freq= 0):
    
    '''
    SUMMARY
    Same as above but includes tau P arrivals plotted with AK135
    has to have an attached event
    '''
    #Imput the arrivals estimated by taup using ak135
    model = TauPyModel(model = 'ak135')

    fig, axs = plt.subplots(len(st), 2, figsize=(30, 5*len(st)))
    fig.subplots_adjust(hspace=0.5)
    
    for ax, tr in zip(axs[:,0], st):
        arrivals= model.get_travel_times (source_depth_in_km = tr.stats.sac.evdp,
                                          distance_in_degree = tr.stats.sac.gcarc,
                                          phase_list=['ttbasic'],
                                          receiver_depth_in_km=1.5) #see deep wiki doc for exact phases
                                            #estimating arrival times for that trace
        #Keeping the earliest arrivals of each phase
        first_arrivals = {}

        for arrival in arrivals:
            if arrival.name not in first_arrivals:
                first_arrivals[arrival.name] = arrival
                                 
        first_arrivals = list(first_arrivals.values())

        t = tr.times()  # Time in seconds relative to trace start
        ax.plot(t, tr.data, color='red')
        ax.grid()
        ax.set_title('Raw')
        ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
        ax.set_ylabel('Counts')
        
        #Calculating arrival times and adding// Inefficient
        n=0
        n1=0
        for i in range(len(arrivals)):
            t = first_arrivals[i].time
            t = t + tr.stats.sac.o
            # correction for being 1.5km bellow sea of 0.7 given 1s if entire water and 0.27 quicker if solid
            t = t+1
            
            if t>250:
                break # so later arrivals not shown
            elif t<0:
                n1=n1+1 # so not regestered diffracted arrivals not shown
                continue
            else:
                ax.axvline(x=t, linestyle='--',color='black')
                n=n+1
                
        phase_names = [first_arrival.name for first_arrival in first_arrivals[n1:n]]
                
        ax.annotate(phase_names,xy=(0, 1),xycoords='axes fraction',ha='left',va='top')

        
    for ax, tr in zip(axs[:,1], st_filt):
        arrivals= model.get_travel_times (source_depth_in_km = tr.stats.sac.evdp,
                                          distance_in_degree = tr.stats.sac.gcarc,
                                          receiver_depth_in_km=1.5) #see deep wiki doc for exact phases
                                            #estimating arrival times for that trace
        #Keeping the earliest arrivals of each phase
        first_arrivals = {}

        for arrival in arrivals:
            if arrival.name not in first_arrivals:
                first_arrivals[arrival.name] = arrival
                                 
        first_arrivals = list(first_arrivals.values())
        t = tr.times()  # Time in seconds relative to trace start
        ax.plot(t, tr.data)
        ax.grid()
        ax.set_title('Filtered')
        ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
        n=0
        n1=0
        for i in range(len(arrivals)):
            t = first_arrivals[i].time
            t = t + tr.stats.sac.o
            # correction for being 1.5km bellow sea of 0.7 given 1s if entire water and 0.27 quicker if solid
            t = t+1
            
            if t>250:
                break # so later arrivals not shown
            elif t<0:
                n1=n1+1 # so not regestered diffracted arrivals not shown
                continue
            else:
                ax.axvline(x=t, linestyle='--',color='black')
                n=n+1
                
        phase_names = [first_arrival.name for first_arrival in first_arrivals[:n]]
                
        ax.annotate(phase_names,xy=(0, 1),xycoords='axes fraction',ha='left',va='top')

    #Creating a title between each row
    fe = FlinnEngdahl()
    
    ## Seperates unidentified and identified cuz titles different 
  
    if filt_type == 'bandpass':
        for i, tr in enumerate(st):
            region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)

            y = axs[i,0].get_position().y1 +0.01 # just above row
            fig.text(
                0.5,
                y,
                f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | station depth= {tr.stats.sac.stdp:.0f} | region= {region} | Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km |\n Dist = {tr.stats.sac.gcarc:.1f} | SNR= {tr.stats.sac.user0} | Demean + Detrend + taper | Filtering method= {filt_type} | Freq = {freq_min:.1f}-{freq_max:.1f} Hz | TauP model = AK135',
                ha='center', # Need to include distance 
                fontsize=15
            )
    else:
        for i, tr in enumerate(st):
            region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)
    
            y = axs[i,0].get_position().y1 +0.01 # just above row
            fig.text(                       
                0.5,
                y,
                f'Date={str(tr.stats.starttime)[:10]} | station={tr.stats.station} | station depth= {tr.stats.sac.stdp:.0f} | region= {region} | Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km |\n Dist = {tr.stats.sac.gcarc:.1f} | SNR= {tr.stats.sac.user0} | Demean + Detrend + taper | filtering method= {filt_type} | Freq = {freq:.1f} hz | TauP model = AK135',
                ha='center', # Need to include distance 
                fontsize=15
            )


    plt.show()



# %% Calculating and ploting a spectrogram
from scipy.signal import spectrogram
from matplotlib.gridspec import GridSpec
from matplotlib.ticker import ScalarFormatter


fe = FlinnEngdahl()
# Fe outside to speed up plots
def spectrogram_plot(st,freq_maximum, freq_minimum, freq_max2=0, freq_min2=0,
                     nfft=252,taper=('tukey',0.25),arrivals=['ttbasic'],
                     log=False,spec_freq_minimum=0.1,spec_freq_maximum=5,
                     perc = [10,99],filter_method='bandpass'
                     ):
    
    '''
    Describe the parameters
    - st is a sac stream object has to be for data with attached events as TauP is calculated and plotted
    - freq_maximum: max freq for first filter
    - freq_minimum: min freq for first filter 
    
    - Perc is the power percentile so bottom 10% and top 1% as default to reduce impact of noise and make spec more readbale
    
    Can plot multiple bandpasses if a freq2 is entered
    
    Rememper plt after is needed
    Want nfft to be around sample time length as pltos best balance of freq and time block size [rec tr length/samplign rate]
    taper defult tukey
    
    RETURNS
    THe figure to do changes after
    All_arrivals: taup arrival time of all arrivals measured for the quake 
    
    '''
    #Obtaining filtered
    if freq_max2==0:
        st_filt = st.copy()
        basic_proc(st_filt)
        st_filt = st_filt.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?
    else:
        st_filt1 = st.copy()
        basic_proc(st_filt1)
        st_filt1 = st_filt1.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?
        
        st_filt2 = st.copy()
        basic_proc(st_filt2)
        st_filt2 = st_filt2.filter(filter_method, freqmax = freq_max2, freqmin = freq_min2) # auto does 1 pass so affects shape?
    st_spec = st.copy()
    
    st_spec.detrend('linear')
    st_spec.detrend('demean')
    tr=st_spec[0]

    x = tr.data
    fs = tr.stats.sampling_rate
    
    #Obtaining first arrivals
    all_arrivals,plot_arrivals=taup_arrivals(tr,arrivals=arrivals)
    
    # Block number minimum should be data length/ samples which is wondow length
    f,t,Sxx = spectrogram(
        x,fs,
        detrend=False,
        scaling='density',
        window=taper,
        nperseg = nfft,
        nfft = nfft,
        noverlap = nfft*0.9, # Slighly lower than nfft
        mode='psd'
        
        )
    
    Sxx= 10*np.log(Sxx+10**(-20))
    
    
    vmin,vmax = np.percentile(Sxx, perc)
    
    #Plotting mutiple bandpasses
    if freq_max2==0:
        fig = plt.figure(figsize=(25,20))
        gs = GridSpec(3, 1, figure=fig, height_ratios=[2,0.6,0.6],hspace=0.2)
        ax_big = fig.add_subplot(gs[0, :])      # spans both columns, top row
        ax_small1 = fig.add_subplot(gs[1, :],sharex=ax_big)   # bottom left
        ax_small2 = fig.add_subplot(gs[2, :],sharex=ax_big)   # bottom right
    else:
        fig = plt.figure(figsize=(25,25))
        gs = GridSpec(4, 1, figure=fig, height_ratios=[2,0.6,0.6,0.6],hspace=0.2)
        ax_big = fig.add_subplot(gs[0, :])      # spans both columns, top row
        ax_small1 = fig.add_subplot(gs[1, :],sharex=ax_big)   # bottom left
        ax_small2 = fig.add_subplot(gs[2, :],sharex=ax_big)   # bottom right
        ax_small3 = fig.add_subplot(gs[3, :],sharex=ax_big)   # bottom right

        
    spec =ax_big.pcolormesh(t, f, Sxx, shading='nearest',
                   vmin=vmin, vmax=vmax,
                   cmap='plasma',
                   )
    ax_big.set_ylabel('Frequency [Hz]')
    ax_big.set_xlabel('Time [sec]')
    ax_big.tick_params(axis='x', pad=10) # So tick label dont overlap with arrivals
    ax_big.set_ylim(0.1,5)
    ax_big.set_xticks(np.arange(0,max(t),25))
    ax_big.set_xlim(min(tr.times()),max(tr.times())) # as due to ft and taper doesnt start at original time
    #If want log 
    if log ==True:
        ax_big.set_yscale('log') 
        ax_big.set_yticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5])
        ax_big.yaxis.set_major_formatter(ScalarFormatter())
    
    for arrival in plot_arrivals: #Plotting the arrival
        ar_t = arrival.time
        ar_t = ar_t + tr.stats.sac.o
        
        length_t=tr.stats.npts/20

        if ar_t>length_t:
            break # so later arrivals not shown
        elif ar_t<0:
            # so not regestered diffracted arrivals not shown
            continue
        else:
            ax_big.axvline(ar_t,linestyle='--',color='red',label=f'{arrival.name}')
            ax_big.text(
                ar_t, -0.025,arrival.name, color='purple', transform=ax_big.get_xaxis_transform() )

    
    region = fe.get_region(tr.stats.sac.evlo, tr.stats.sac.evla)
    ax_big.set_title(f'Spectrogram of event\n  Date={str(tr.stats.starttime)[:13]} | station={tr.stats.station} | region= {region} | Mag={tr.stats.sac.mag:.2f} | EQ Depth={tr.stats.sac.evdp:.1f} km | Dist = {tr.stats.sac.gcarc:.1f} \n parameters: nfft={nfft} | Power percentile={perc} | taper={taper} | freq lim= {spec_freq_minimum} - {spec_freq_maximum} Hz | arrivals taup model ak135',
                     fontsize=20)
    ax_big.set_ylim(spec_freq_minimum,spec_freq_maximum)
    cax = fig.add_axes([0.92, 0.55, 0.02, 0.33]) # [left, bottom, width, height]
    cbar=fig.colorbar(spec,ax=ax_big,pad=0.01,cax=cax)
    cbar.set_label(r'Power spectral density $\log (\frac{\text{counts}^2}{Hz})$', fontsize=20)
    
    if freq_max2==0:
        singleplot_filt_arrivals(st, st_filt,filter_method,axs=[ax_small1,ax_small2],fig=fig ,freq_max=freq_maximum,freq_min=freq_minimum, show=False,title=False,
                             arrivals=arrivals)
    else:
        singleplot_filt_arrivals_multiband(st, st_filt1,st_filt2,axs=[ax_small1,ax_small2,ax_small3],fig=fig ,freq_max1=freq_maximum,freq_min1=freq_minimum,
                                   freq_max2=freq_max2,freq_min2=freq_min2,show=False,title=False, arrivals=arrivals)
    
    return fig, all_arrivals

# %%

def spectrogram_plot_uni(st,freq_maximum, freq_minimum, freq_max2=0, freq_min2=0,
                     nfft=252,taper=('tukey',0.25),
                     log=False,spec_freq_minimum=0.1,spec_freq_maximum=5,
                     perc = [10,99],filter_method='bandpass',add_map=False):
    
    '''
    Describe the parameters
    
    ALl same as the one above but NO TAUP calculated 
    So works also with unidentified events and all sac files
    AGAIN TO MYSELF WORKS WITH ALL SEISMOGRAMS IN SAC FORMAT 
    '''
    #Obtaining filtered
    filter_method='bandpass'
    
    #Obtaining filtered
    if freq_max2==0:
        st_filt = st.copy()
        basic_proc(st_filt)
        st_filt = st_filt.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?
    else:
        st_filt1 = st.copy()
        basic_proc(st_filt1)
        st_filt1 = st_filt1.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?
        
        st_filt2 = st.copy()
        basic_proc(st_filt2)
        st_filt2 = st_filt2.filter(filter_method, freqmax = freq_max2, freqmin = freq_min2) # auto does 1 pass so affects shape?ilter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

    
    st_spec = st.copy()
    
    st_spec.detrend('linear')
    st_spec.detrend('demean')
    tr=st_spec[0]

    x = tr.data
    fs = tr.stats.sampling_rate
    
    # Block number minimum should be data length/ samples which is wondow length
    f,t,Sxx = spectrogram(
        x,fs,
        detrend=False,
        scaling='density',
        window=taper,
        nperseg = nfft,
        nfft = nfft,
        noverlap = nfft*0.9, # Slighly lower than nfft
        mode='psd'
        
        )
    
    Sxx= 10*np.log(Sxx+10**(-20))
    
    perc = [10,99]
    vmin,vmax = np.percentile(Sxx, perc)
    #Plotting mutiple bandpasses
    
    if freq_max2==0:            
        fig = plt.figure(figsize=(25,20))
        gs = GridSpec(3, 1, figure=fig, height_ratios=[2,0.6,0.6],hspace=0.2)
        ax_big = fig.add_subplot(gs[0, :])      # spans both columns, top row
        ax_small1 = fig.add_subplot(gs[1, :],sharex=ax_big)   # bottom left
        ax_small2 = fig.add_subplot(gs[2, :],sharex=ax_big)   # bottom right
        
            
    else:
        fig = plt.figure(figsize=(25,25))
        gs = GridSpec(4, 1, figure=fig, height_ratios=[2,0.6,0.6,0.6],hspace=0.2)
        ax_big = fig.add_subplot(gs[0, :])      # spans both columns, top row
        ax_small1 = fig.add_subplot(gs[1, :],sharex=ax_big)   # bottom left
        ax_small2 = fig.add_subplot(gs[2, :],sharex=ax_big)   # bottom right
        ax_small3 = fig.add_subplot(gs[3, :],sharex=ax_big)   # bottom right

    spec =ax_big.pcolormesh(t, f, Sxx, shading='nearest',
                   vmin=vmin, vmax=vmax,
                   cmap='plasma',
                   )
    ax_big.set_ylabel('Frequency [Hz]')
    ax_big.set_xlabel('Time [sec]')
    ax_big.tick_params(axis='x', pad=10) # So tick label dont overlap with arrivals
    ax_big.set_ylim(0.1,5)
    ax_big.set_xticks(np.arange(0,max(t),25))
    ax_big.set_xlim(min(tr.times()),max(tr.times())) # as due to ft and taper doesnt start at original time
    #If want log 
    if log ==True:
        ax_big.set_yscale('log') 
        ax_big.set_yticks([0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1,2,3,4,5])
        ax_big.yaxis.set_major_formatter(ScalarFormatter())    
    #To inclide SNR wich is unique mermaid header
    if tr.stats.network == 'MERMAID':
        ax_big.set_title(f'Spectrogram unidentified \n  Date={str(tr.stats.starttime)[:13]} | station={tr.stats.station} | SNR ={tr.stats.sac.user0:.3f} \n parameters: nfft={nfft} | Power percentile={perc} | taper={taper} | freq lim= {spec_freq_minimum} - {spec_freq_maximum} Hz |',
                     fontsize=20)
    else:
        ax_big.set_title(f'Spectrogram \n  Date={str(tr.stats.starttime)[:13]} | station={tr.stats.station} \n parameters: nfft={nfft} | Power percentile={perc} | taper={taper} | freq lim= {spec_freq_minimum} - {spec_freq_maximum} Hz |',
                     fontsize=20)
    ax_big.set_ylim(spec_freq_minimum,spec_freq_maximum)
    cax = fig.add_axes([0.92, 0.55, 0.02, 0.33]) # [left, bottom, width, height]
    cbar=fig.colorbar(spec,ax=ax_big,pad=0.01,cax=cax)
    cbar.set_label(r'Power spectral density $\log (\frac{\text{counts}^2}{Hz})$', fontsize=20)

    if freq_max2==0:
        singleplot_filt(st, st_filt,filter_method,axs=[ax_small1,ax_small2],fig=fig ,freq_max=freq_maximum,freq_min=freq_minimum, show=False,title=False,
                             )
    else:
        singleplot_filt_multiband(st, st_filt1,st_filt2,axs=[ax_small1,ax_small2,ax_small3],fig=fig
                                  ,freq_max1=freq_maximum,freq_min1=freq_minimum,
                                  freq_max2=freq_max2,freq_min2=freq_min2
                                  ,show=False,title=False,
                             )
                  
    if add_map:
        mer_df=mermaid_df(st)
        reciever_loc_unid(mer_df,ax=ax_right,fig=fig,title=False)
        
    return fig

# %%


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

