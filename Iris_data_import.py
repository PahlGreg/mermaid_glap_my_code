#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 19 10:28:49 2026

@author: gregory

Code for importing data
"""
from obspy import UTCDateTime
import obspy
from obspy import read
from obspy.clients.fdsn import Client
from obspy.clients.fdsn import RoutingClient
import matplotlib.pyplot as plt

def get_waveform_mseed(network,station,channel,starttime,endtime,
                     client='EARTHSCOPE',location='00'):
    '''
    Get the waveform in a stream file in Mseed format 
    SAC not supported for Earthscope
    '''
    client = Client(client)
    st = client.get_waveforms(network, station,location ,channel, starttime, endtime)
    
    return st
# %%

client = Client('EARTHSCOPE')

network='IU'
station='PAYG'
channel='*'
location ='00'
starttime=UTCDateTime("2015-01-20T07:01")
endtime= UTCDateTime('2015-01-21T07:06')

st = client.get_waveforms(network, station,location ,channel, starttime, endtime)
# %%



client = Client('EARTHSCOPE')

network='IU'
station='PAYG'
channel='*'
location ='00'
starttime=UTCDateTime("2015-01-20T07:01")
endtime= UTCDateTime('2015-01-21T07:06')
st1 = client.get_waveforms(network, station,location ,channel, starttime, endtime)


st1[0].write('event.sac', format='SAC')

st+=read('event.sac')
print(st)

# %%

from my_code.mer_plot_f import spectrogram_plot_land
freq_maximum = 5
freq_minimum =2
spec_freq_maximum = 10
spec_freq_minimum = 0.1
nfft = int(st[0].stats.npts/20)

spectrogram_plot_land(st,freq_maximum,freq_minimum,
                      spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum
                      ,nfft=nfft)

# %% Search for events

def get_earthquakes(client='EARTHSCOPE',**kwargs):
    allowed = {starttime, endtime, minlatitude, maxlatitude, minlongitude, maxlongitude, 
               latitude, longitude, minradius, maxradius, mindepth, maxdepth, minmagnitude,
               maxmagnitude, magnitudetype, eventtype, includeallorigins, includeallmagnitudes, includearrivals, 
               eventid, limit, offset, orderby, catalog, contributor, updatedafter, filename}
    filtered = {k: v for k, v in kwargs.items() if k in allowed}
    client=Client(client)
    cat = client.get_events(**filtered)
    return cat
    

client = Client("EARTHSCOPE")
starttime = UTCDateTime("2015-02-27T06:30:00.000")
endtime = starttime + 360*60
maxmagnitude = 6
minmagnitude = 4
event_params = {
    "starttime": UTCDateTime("2023-01-01"),
    "endtime": UTCDateTime("2023-01-02"),
    "minmagnitude": 5.0,
}
cat = get_earthquakes(starttime,endtime,maxmagnitude,minmagnitude)
print(cat)