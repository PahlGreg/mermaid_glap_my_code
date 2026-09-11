#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 14:37:58 2026

@author: gregory
"""

import sys
sys.path.append('/home/gregory/Documents/mermaid_glap')

import obspy
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from obspy.geodetics import FlinnEngdahl #for getting quake location
from my_code.mer_plot_f import spectrogram_plot
from my_code.mer_plot_f import spectrogram_plot_uni 



print('Plotting a certain spectrogram from MERMAID data')
if_id = input('Plot identified event (y/n)? ') or 'y'
if if_id == 'y':
    if_id = 'i'
elif if_id == 'n':
    if_id = 'uni'
else:
    raise ValueError('Enter y/n')

sac_name = input('Enter the MERMAID and date of event, give hour if multiple'
                 'format [m##.YYYYMMDD*HH] : m') or '10.201406'
datafile = f'data/galapagos/mermaid*/{if_id}dentified/sac/m{sac_name}*.sac'
st= read(datafile)
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

        
spec_freq_maximum = float(input('Spectrogram max frequency (hz): ') or 5)
spec_freq_minimum = float(input('Spectrogram min frequency (hz): ') or 0.1)

if (input('Change other options (y/n)? ') or 'n') == 'n':
    freq_maximum= 2.5
    freq_minimum=0.5
    freq_max2 = 10
    freq_min2 = 2.5
    nfft = int(len(st[0].data)/20)
    taper = ('tukey',0.25)
    arrivals = ['ttbasic']
else:
    freq_maximum=float(input('Filtered seismogram max freqency: ') or 2.5)
    freq_minimum=float(input('Filtered seismogram min freqency: ') or 0.5)
    freq_max2 = float(input('Second filtered seismogram max freqency: ') or 0)
    freq_min2 = float(input('Second filtered seismogram min freqency: ') or 0)
    nfft = int(input('window number (nfft): ') or (int(len(st[0].data)/20)))
    
    arrivals = [input('TauP phase arrivals wanted: ') or 'ttbasic']


if if_id =='n':

    fig = spectrogram_plot_uni(
        st[0:1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
        spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
        nfft=nfft,
        log=log,
        taper=taper
        )
    plt.show()

else:
    fig,arrivals = spectrogram_plot(
        st[0:1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
        spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
        arrivals=arrivals,
        nfft=nfft,
        log=log,
        taper=taper
        )
    plt.show()