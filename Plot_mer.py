#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 21 11:45:50 2026

@author: gregory

Parts of this code

- single_plot: Function to plot a single raw trace from a stream 
- singleplot_filt: Function to plot single raw trace and filter it with both raw and filtered
- multiplot_filt: Function that plots multiple filtered plots of above
- basic_proc: Function that demean+detrends + tapers
- multiplot_filt_arrivals: plots multiplot_filt but includes a tauP phase estimate

- code which selects certain streams according to a criteria and 
    applys a bandpass
- Code Broken to plot sta/lta
- Code that goes though various frequency bands with small steps at the beginning
- Code that estimates tauP then use mult_arrivals to plot them
- Code that tries to remove instrement responce, not finished

- Bunch os spectrogram code options ie
- Plot single, multiple spectrograms and even save them 
- choice of 2 filtered seismograms bellow 
-

- Code that identifies the seismoframs taht triggered within an house of each other outputting the times and sations 
- Code that pltos mermaid data as a spectrogram with many options
- Code bellow is the same but with the different spec options ie a second filted, log, identified and unidentified 
- CODE makes into df mermaid data
- CODE 
"""

import obspy
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
from obspy import Stream
from matplotlib.ticker import MultipleLocator


# %% Single plot function



st = read('data/galapagos/mermaid*/*identified/sac/m*.20140906*sac')


# %% Multiplots script
from obspy.geodetics import FlinnEngdahl
import obspy.signal
from obspy.taup import TauPyModel


from my_code.mer_plot_f import singleplot_filt,multiplot_filt, basic_proc,singleplot_filt, singleplot_filt_arrivals,multiplot_filt_arrivals
from my_code.mer_plot_f import spectrogram_plot, taup_arrivals
from my_code.mer_data_invst_f import loc_spectro




# %% Select certain events 
from obspy import Stream

'''
This is the code to select certain quakes and create a list of the
'''
st = read('data/galapagos/mermaid*/identified/sac/m10.201505*.sac')

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

# %% Plotting the unfiltered 

'''
One of th best wats to filter is the SNR 

'''
st = read('data/galapagos/mermaid*/*identified/sac/m*.2015012*.sac')

st1_filt = st.copy()
ref_trace = st1_filt[0]  # 

ref_max = np.max(np.abs(ref_trace.data))

for tr in st1_filt:
    tr.data = tr.data / ref_max
basic_proc(st1_filt)
freq_maximum = 10
freq_minimum =5

#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'
st1_filt = st1_filt.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

fig,axs = multiplot_filt(st,st1_filt,filt_type='bandpass', freq_max = freq_maximum, freq_min = freq_minimum)
for ax in axs[1:,1]:
    ax.sharey(axs[0,1])
plt.show()


# %% Reproducing long term avergae/ short term average
st = read('data/galapagos/mermaid10/identified/sac/m10.2015*.sac')
# Ive fucked this
tr1 = st1_filt.copy() # Dont work at the moment??????
ratio = tr1.trigger('classicstalta', sta = 20, lta = 50)

st[0].plot()
ratio.plot()

# %% Creating a loop to examine effectiveness of different band pass filters


# Fine increments from 0.1 to 1.0
from mer_plot_f import band_analysis
st = read('data/galapagos/mermaid*/identified/sac/m10.2014*.sac')
band_analysis(st)

# st = read('data/galapagos/mermaid*/identified/sac/m26.201608*.sac')
# band_analysis(st)


# %% Calculating a taup
from obspy.taup import TauPyModel
st = read('data/galapagos/mermaid*/identified/sac/m*.20150120*.sac')

st1 = st.copy()
st1 = basic_proc(st1)
tr= st[0]

model = TauPyModel(model = 'ak135')

freq_maximum = 5
freq_minimum =0.7
#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'
st1 = st1.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

multiplot_filt_arrivals(st, st1, filter_method, freq_max = freq_maximum, freq_min = freq_minimum)
# arr1 = arrP.time + st1[0].stats.sac.o
# arr2 = arr_2.time + st1[0].stats.sac.o
# arr3 = arr_3.time + st1[0].stats.sac.o


# %% Removing instrument responce

'''
Doesnt work wrong poles and zeros 
'''
from obspy import read_inventory

st = read('data/galapagos/mermaid*/identified/sac/m10.20140629*.sac')
tr=st[0]

tr.plot()
MH = {'poles': [ (+5.015100e-02+5.040500e-02j),
	(+5.015100e-02-5.040500e-02j),
	(+4.924900e-02+5.933400e-04j),
	(+4.924900e-02-5.933400e-04j),
	(-7.288200e-01+0.000000e+00j),
	(-5.839700e-02+8.598600e-05j),
	(-5.839700e-02-8.598600e-05j) ],
      'sensitivity' :  -1.494000e+05, #PA,
      'gain' : 1.0,
      'zeros' : [ (	+4.981300e-02+4.892900e-02j),
	(+4.981300e-02-4.892900e-02j),
	(+5.527100e-02+4.531600e-02j),
	(+5.527100e-02-4.531600e-02j),
	(-2.368800e-02+3.887800e-02j),
	(-2.368800e-02-3.887800e-02j),
	(+0.000000e+00+0.000000e+00j) ]
  }
st.simulate(paz_remove=MH)

st.plot()
# %% manual taup calc


# %% Single plot tau p arrivals
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

arrivals,first_arrivals=singleplot_filt_arrivals(st,st1_filt,filter_method,arrivals=['P','PcP'])

print(first_arrivals[0].time)




# %% Plotting spectrograms and saving



datapath='data/galapagos/mermaid*/identified/sac/m*.20160410*.sac'
datafile= datapath[-17:]
st = read(datapath)
# freq_maximum = 5
# freq_minimum =2
# spec_freq_maximum = 5
# spec_freq_minimum = 0.1
# #Filters, frequency
#Before filtering detrend and de mean

# spectrogram_plot(st, freq_maximum, freq_minimum)
# for i in range(len(st)):
#     fig, all_arrivals = spectrogram_plot(st[i:i+1], freq_maximum, freq_minimum,
#                                          spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
#                                          arrivals=['ttbasic'],nfft=nfft,log=False)
#     plt.show()
#     t= UTCDateTime(st[i].stats.starttime)
#     time= t.strftime("%Y%m%dT%H%M%S")
#     station=st[i].stats.station
#     fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/Glap_spec/m{station}.{time}.png', dpi=300, bbox_inches='tight')

freq_maximum = 10
freq_minimum =4
spec_freq_maximum = 10
spec_freq_minimum = 0.1
for i in range(len(st)):
        
    nfft = int(len(st[i].data)/20)

    fig, all_arrivals = spectrogram_plot(st[i:i+1], freq_maximum, freq_minimum,
                                         spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
                                         arrivals=['ttbasic'],nfft=nfft,log=False,taper=('tukey',0.25)
                                         )
    plt.show()
    t= UTCDateTime(st[i].stats.starttime)
    time= t.strftime("%Y%m%dT%H%M%S")
    station=st[i].stats.station
    
    fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/spectrograms/Interesting_spec/reverb_spec/m{station}.{time}_rev.png', dpi=300, bbox_inches='tight')

# %% Addign arrivals and times as predicted by tauP
# This just plots a single specrogram without saving 
st = read('data/galapagos/mermaid*/identified/sac/m25*.20140720*.sac')


freq_maximum=2
freq_minimum=0.5
spec_freq_maximum = 10
spec_freq_minimum = 0.1
freq_max2 = 9
freq_min2 = 7
nfft = int(len(st[0].data)/20)

fig,arrivals = spectrogram_plot(
    st,freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
    spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
    arrivals=['ttbasic'],
    nfft=nfft,
    log=False,
    taper=('tukey',0.25)
    )


print(arrivals)
print('start of seismogram after event:',st[0].stats.sac.o)

# %% Multiplot spectrogram

st = read('data/galapagos/mermaid*/identified/sac/m*.20160425T07*.sac')

freq_maximum=10
freq_minimum=6
spec_freq_maximum = 10
spec_freq_minimum = 0.1

for i in range(len(st)):
    nfft = int(len(st[i].data)/20)
    nfft = 200

    fig, all_arrivals = spectrogram_plot(st[i:i+1], freq_maximum, freq_minimum,
                                         spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
                                         arrivals=['ttbasic'],nfft=nfft,log=False,taper=('tukey',0.5)
                                         )
    plt.show()



# %% Code to only save certain spectrograms 
st = read('data/galapagos/mermaid*/identified/sac/m*.*.sac')
from obspy import Stream

st = Stream(
    tr for tr in st
    # if tr.stats.sac.mag >= 5.0 and tr.stats.sac.mag >=6 
    # if tr.stats.sac.gcarc >=140 and tr.stats.sac.gcarc <=180 #For tele
    if tr.stats.sac.gcarc <=3
    )

freq_maximum=2
freq_minimum=0.5
spec_freq_maximum = 5
spec_freq_minimum = 0.1
freq_max2 = 10
freq_min2 = 2.5

# arrivals_list=['PKP','PKIKP','pPKIKP']
arrivals_list=['ttbasic']
for i in range(len(st)):
        
    nfft = int(len(st[i].data)/20)

    fig,arrivals = spectrogram_plot(
        st[i:i+1],freq_maximum, freq_minimum, freq_min2=freq_min2, freq_max2=freq_max2,
        spec_freq_maximum=spec_freq_maximum,spec_freq_minimum=spec_freq_minimum,
        arrivals=arrivals_list,
        nfft=nfft,
        log=False,
        taper=('tukey',0.25)
        )
    
    plt.show()
    # t= UTCDateTime(st[i].stats.starttime)
    # time= t.strftime("%Y%m%dT%H%M%S")
    # station=st[i].stats.station
    # # Remember ti change save location
    # fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/spectrograms/search_for_rumblings/m{station}.{time}.png', dpi=200, bbox_inches='tight')
    
# %% Claculating own arrivals of a event and plotting 
st=read('data/galapagos/mermaid*/*identified/sac/m*.20150323*.sac')

from obspy.geodetics import locations2degrees

event_coord = (-18.353, -69.166)
event_depth = 130
event_starttime = UTCDateTime('2015-03-23 04:51:38 ')
for tr in st:
    coord_1 = (tr.stats.sac.stla, tr.stats.sac.stlo)
    arc = locations2degrees(lat1= coord_1[0], 
                            long1= coord_1[1],
                            lat2 = event_coord[0],
                            long2= event_coord[1]
                            )
    tr.stats.sac.gcarc = arc
    tr.stats.sac.evdp = event_depth
    
    time_diff = UTCDateTime(tr.stats.starttime) - event_starttime
    tr.stats.sac.o = time_diff
    

st1 = st.copy()
st1 = basic_proc(st1)
tr= st[0]

model = TauPyModel(model = 'ak135')

freq_maximum = 5
freq_minimum =0.7
#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'
st1 = st1.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?

multiplot_filt_arrivals(st, st1, filter_method, freq_max = freq_maximum, freq_min = freq_minimum)



# %% Assessing the datas mutliple mermaids saw an event 
from obspy import Stream
from my_code.mer_data_invst_f import mermaid_df, events_seen

st = read('data/galapagos/mermaid*/unidentified/sac/m*.*.sac')

    
# st = Stream(
#     tr for tr in st
#     # if tr.stats.sac.mag >= 5.0 and tr.stats.sac.mag >=6 
#     # if tr.stats.sac.gcarc >=140 and tr.stats.sac.gcarc <=180 #For tele
#     if tr.stats.sac.gcarc <=2
#     )


mer_df = mermaid_df(st)

event_times = events_seen(mer_df)

df = event_times.groupby('count').size()

# %% Saving loc ana spec of these
st = read('data/galapagos/mermaid*/*identified/sac/m*.sac')

for i in range(len(event_times['start_time'])):
    if event_times['count'][i] == 5:
        loc_spectro(st,(event_times['start_time'][i]),(event_times['end_time'][i]))
    else:
        continue

# %% Plotting nearb triggers seismograms on same plot


fig, ax = plt.subplots(figsize=(15, 5))

refancet= UTCDateTime(mer_df['starttime'].min())

for tr in st:
    t = tr.times(reftime=refancet)
    data = tr.data / np.max(np.abs(tr.data)) * 20 # Normalise and scale might be better method
    ax.plot(t,data+tr.stats.sac.gcarc)

plt.show()

# %% Plotting a record section not including distance 

st = read('data/galapagos/mermaid*/*identified/sac/m*.20150117T*.sac')
st.normalize(global_max=True)
n = len(st)
fig, ax =  plt.subplots(figsize=(15,1*n),sharey=True)


#De trend and demean
basic_proc(st)

freq_maximum = 10
freq_minimum =5
#Filters, frequency
#Before filtering detrend and de mean
filter_method = 'bandpass'

st = st.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum)

starttime_all = min(tr.stats.starttime for tr in st)
endtime_all = max(tr.stats.endtime for tr in st)
stations = sorted(set(tr.stats.station for tr in st))

offset = 0
spacing = 10 * st[0].data.std() # not sure i agree with this

for tr in st:
    times = tr.times(reftime=starttime_all)
    ax.plot(times,tr.data + offset, 'darkblue', linewidth=0.7)
    ax.text(times[0],offset,tr.id, fontsize=8, va='center', ha='right'),
    offset += spacing

ax.set_xlabel("Time (s)")
ax.set_yticks([])
ax.set_title(f'Seismic section | Time frame={str(starttime_all)[:16]} - {str(endtime_all)[:16]}  |\n station={stations} |  Demean + Detrend + taper + normalised | filtering method= {filter_method} | freq = {freq_minimum:.1f}-{freq_maximum:.1f} Hz')

ax.xaxis.set_major_locator(MultipleLocator(50))
ax.xaxis.set_minor_locator(MultipleLocator(10))
# Grid lines for both
ax.grid(which='major', axis='x', linewidth=0.8, color='gray')
ax.grid(which='minor', axis='x', linewidth=0.4, color='lightgray', linestyle='--')

plt.tight_layout()

plt.show()
#
    


    
