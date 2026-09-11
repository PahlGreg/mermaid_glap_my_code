#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 10:46:46 2026

@author: gregory
"""
from obspy import read
from obspy.clients.fdsn import Client
from obspy import UTCDateTime


def iris_import(st,length='all'):
    '''
    Imports a stream file
    Has options for a different station currently on PAYG Galapagos
    
    Reads the max and min time (either entire or single trace)
    imports PAYG data from around that period 
    Adds it to the stream after saving

    '''
    network='IU'
    station='PAYG'
    channel='*'
    location ='00'
    client = Client('EARTHSCOPE')

    if length=='all':
        starttime_all = min(tr.stats.starttime for tr in st)
        endtime_all = max(tr.stats.endtime for tr in st)
        starttime=UTCDateTime(starttime_all)
        endtime= UTCDateTime(endtime_all)
        st1 = client.get_waveforms(network, station,location ,channel, starttime, endtime)
        st1[0].write('event.sac', format='SAC')
            # writes to a event file to get in sac format then is read in and added to the stream
        st+=read('event.sac')


    else:
        for tr in st:
            starttime = (tr.stats.starttime)
            endtime = (tr.stats.endtime)
            starttime=UTCDateTime(starttime)
            endtime= UTCDateTime(endtime)
            st1 = client.get_waveforms(network, station,location ,channel, starttime, endtime)
            st1[0].write('event.sac', format='SAC')
            
            st+=read('event.sac')

    return st
