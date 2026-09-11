#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  7 11:09:44 2026

@author: gregory
"""
from my_code.mer_plot_f import multiplot_filt, basic_proc
import obspy
from obspy import Stream
from obspy import read
import matplotlib.pyplot as plt

'''
This is the code to select certain quakes and create a list of the
'''
st = read('data/galapagos/mermaid*/identified/sac/m*.sac')

# Add lines to this code/ unindenti it
st = Stream(
    tr for tr in st
    # if tr.stats.sac.mag >= 5.0 and tr.stats.sac.mag >=6 
    if tr.stats.sac.gcarc <3
    )


st1_filt = st.copy()

#De trend and demean
basic_proc(st1_filt)

freq_maximum = 5
freq_minimum =0.8
#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'
st1_filt = st1_filt.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

multiplot_filt(st,st1_filt,filt_type='bandpass', freq_max = freq_maximum, freq_min = freq_minimum)
plt.show()