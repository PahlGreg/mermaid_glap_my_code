#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 10:26:39 2026

@author: gregory
"""

'''
SUMMARY
Aims to be a quick access to basic code for plots that ive created when you input a sac file
'''

import obspy
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
from obspy import Stream

from my_code.mer_plot_f import singleplot_filt,multiplot_filt, basic_proc,singleplot_filt, singleplot_filt_arrivals,multiplot_filt_arrivals
from my_code.mer_plot_f import spectrogram_plot_uni, spectrogram_plot_uni
# %%

st = read('data/galapagos/mermaid*/*identified/sac/m*.20150124*.sac')

# %% Read and select only certian events # %% Plotting multiple seismograms with afiltered and nonfiltered

'''
READS 
CAN SELECT CERTAIN IDENTIFIED OR LEAVE BLANK FOR UNIDENTIFIED OR ALL 
PLOTS A SINGLE BANDPASS OR CHANGE TO FREQ FOR HIGH PASS
'''
st = read('data/galapagos/mermaid*/identified/sac/m10.201505*.sac')

# # Add lines to this code/ unindenti it
# st = Stream(
#     tr for tr in st
#     if tr.stats.sac.mag >= 5.0 and tr.stats.sac.mag >=6 
# #     # if tr.stats.sac.gcarc <4
#     )

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

# %% Plot 1 seismogram and the tauP arrivals
'''
PLOTS SINGLE IDENTIFIED SEISMOGRAM ACCORDING TO TAUP AK135

IF WANT MULTIPLE CNA USE FOR TR IN ST
'''
st=read('data/galapagos/mermaid*/identified/sac/m22.20150211*.sac')
st1_filt = st.copy()

#De trend and demean
basic_proc(st1_filt)


freq_maximum = 5
freq_minimum =0.8
#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'
st1_filt = st1_filt.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

arrivals,first_arrivals=singleplot_filt_arrivals(st,st1_filt,filter_method, arrivals=['P','PcP'])

print(first_arrivals[0].time)

# %% Single spectogram plot

'''
Simple spectrogram with limited title information #

dont include freq limit 2 if want only 1 band pass
'''

# st = read('/home/gregory/Downloads/SIGNALS/airguns1.sac')

freq_maximum=10
freq_minimum=2.5
spec_freq_maximum = 5
spec_freq_minimum = 0.1
freq_max2 = 10
freq_min2 = 2.5

nfft = int(len(st[0].data)/20)

# freq_min2=freq_min2, freq_max2=freq_max2,
fig = spectrogram_plot_uni(
    st[0:1],freq_maximum, freq_minimum, 
    spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
    nfft=nfft,
    log=False,
    taper=('tukey',0.25)
    )
plt.show()
