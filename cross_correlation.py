#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 14:50:24 2026

@author: gregory
"""
from obspy import Stream, Trace
from obspy.signal import cross_correlation
from obspy.core import UTCDateTime
from obspy import read
import matplotlib.pyplot as plt
import numpy as np
import sys
import pandas as pd
import seaborn as sns
from scipy.signal import find_peaks 

from my_code.mer_plot_f import basic_proc
# %% Makign evelope functions and importing data
from scipy.signal import envelope
from scipy.signal.windows import triang
from scipy.signal import convolve
'''
Better to do on first 50 seconds with limited noise
cc limited noise ask jessica about
'''


def rms_envelope_pandas(signal, fs,ws=10,window='boxcar'):
    window_size = int(ws * fs)
    
    if window=='boxcar':
        s = pd.Series(signal)
        mean_sq = (s**2).rolling(window=window_size, center=True, min_periods=1).mean()
    if window=='triangle':

        n = int(ws * fs)
    
        w = triang(n)
        w /= w.sum()
    
        mean_sq = pd.Series(convolve(signal**2, w, mode='same'))  # numpy array

    return np.sqrt(mean_sq).values

def envelope_and_inpulse(st,ws,freq_minimum=5,freq_maximum=10,normalise=True,impulse=True,second_interval=20,window='boxcar'):
    
    '''
    Takes a trace input and rms i by a window and adds a inpulse if true 
    
    Then outputs a stream of the new values plus filtered orifional strea
    '''
    
    st_wind = st.copy()
    basic_proc(st_wind)
    

    #Filters, frequency
    #Before filtering detrend and de mean
    filter_method = 'bandpass'
    st_wind = st_wind.filter(filter_method, freqmax = freq_maximum, freqmin = freq_minimum) # auto does 1 pass so affects shape?
    if normalise==True:
        st_wind.normalize() #REMEMBER I NORMALISE
    
    envelopes = [rms_envelope_pandas(tr.data, tr.stats.sampling_rate,ws=ws,window=window) for tr in st_wind]
    if impulse==True:
        # Makign impulse responce
        npts = st[0].stats.npts
        dt = 1/st[0].stats.sampling_rate # want it to be same as mermaid data
    
        #creating impulse
        impulse_d=np.zeros(npts)
        interval = int(second_interval/dt) # creating inteval in samples
        impulse_d[::interval] = 1 #impulse center
        pad = npts*4
        
        impulse_d = np.pad(
            impulse_d,
            (pad, pad),
            mode='constant',
            constant_values=0
        )
        tr_delta = Trace(data=impulse_d)
        tr_delta.stats.delta = dt
        tr_delta.stats.station = 'impluse'
        
       
        st_wind.append(tr_delta) # adding to existing stream
        envelopes.append(rms_envelope_pandas(tr_delta.data,tr_delta.stats.sampling_rate, 
                                             ws=ws,window=window))
    st_make=[]
    for env,tr in zip(envelopes,st_wind):
        tr_ev = Trace(data=env)
        tr_ev.stats = tr.stats
        st_make.append(tr_ev)
    
    st_env = Stream(traces=st_make)
    return st_env,st_wind



def cross_correlate(st,ws=3,shift=2000,freq_maximum=10,freq_minimum=5, save_env=False,impulse=False,window='boxcar'):
### Parameters
    
    st_e,st_wind = envelope_and_inpulse(st,ws,freq_maximum=freq_maximum,freq_minimum=freq_minimum,
                                             normalise=True, window=window,impulse=impulse)
    
    from my_code.mer_plot_f import multiplot_filt
    print(st_wind[1].stats)
    print(st_e[1].stats)
    multiplot_filt(st_wind,st_e,filt_type='Envelope',info =False)
    plt.show()
    # ploting the trace and envelope
    if save_env:
        for tr_e,tr in zip(st_e,st_wind):
        
        
            fig, ax = plt.subplots(figsize=(15, 5))
            ax.plot(tr.times(), tr.data, "red",linewidth=0.5)
            ax.plot(tr_e.times(), tr_e.data, "b-")
        
            fig.autofmt_xdate()
            ax.set_xlabel('Time (s)')
            ax.set_ylabel('counts')
            ax.set_title(f'M{tr.stats.station}.{str(tr.stats.starttime)[:10]} trace and envelope')
            ax.grid()
        
            plt.show()
            fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/Show_jessica/09-03_meeting/M{tr.stats.station}.{str(tr.stats.starttime)[:10]}_env.png', dpi=100, bbox_inches='tight')
    # cross correlate signals 
    results = []
    for i in range(len(st_e)):
        # cross_correlation.correlate(tr_delta.data,envelopes[i],shift)
        for j in range(len(st_e)):
    
            cc = cross_correlation.correlate(st_e[i].data,st_e[j].data,shift)
            lag, value = cross_correlation.xcorr_max(cc)
            results.append({
                
                "trace1":str(st_wind[i].id+str(st_wind[i].stats.starttime)[:13]),
                'trace2':str(st_wind[j].id+str(st_wind[j].stats.starttime)[:13]),
                'cc': cc.copy(),
                "lag": lag/20, # div by sample rate to give in time
                "cc_max_value": value
                })
    #Creating plot with ai check it 
    # --- Build DataFrame from your results list ---
    df_results = pd.DataFrame(results)
    
    # --- Pivot into a square matrix: rows/cols = trace names, values = cc_max_value ---
    corr_matrix = df_results.pivot(index="trace1", columns="trace2", values="cc_max_value")
    
    # Optional: keep trace order consistent (e.g. as they appear in st_wind)
    trace_order = [str(tr.id + str(tr.stats.starttime)[:13]) for tr in st_wind]
    corr_matrix = corr_matrix.loc[trace_order, trace_order]
    
    return corr_matrix,df_results,st_e,st_wind

def heat_plot(matrix,label,title,cmap='magma',annotate=True):
    # --- Plot ---
    mask = np.tril(np.ones_like(matrix, dtype=bool), k=-1)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        abs(matrix),
        mask=mask,
        annot=annotate,
        fmt=".2f",
        cmap=cmap,
        vmin=0,
        square=True,
        linewidths=0.5,
        cbar_kws={"label": f"{label}"},
        ax=ax,
    )
    ax.set_title(title)

    n = matrix.shape[0]
    # full grid lines spanning the whole square, ignoring the mask
    ax.hlines(np.arange(n + 1), *ax.get_xlim(), color="grey", linewidth=0.1)
    ax.vlines(np.arange(n + 1), *ax.get_ylim(), color="grey", linewidth=0.1)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
# %%
    

st = read('data/galapagos/mermaid*/*identified/sac/m*.20150120*.sac')
# st += read('data/galapagos/mermaid*/*identified/sac/m*.20150124T13*.sac')
# st += read('data/galapagos/mermaid*/*identified/sac/m*.20150124T14*.sac')
# st += read('data/galapagos/mermaid*/*identified/sac/m*.20150117T18*.sac')
# st += read('data/galapagos/mermaid*/*identified/sac/m*.20150118T03*.sac')

ws=3
shift=2000
freq_maximum=10
freq_minimum=5
save_env=False
window='triangle' # Better correlation with boxcar
corr_matrix,df_results,st_e,st_wind = cross_correlate(st,ws=ws,shift=shift,freq_maximum=freq_maximum,
                                                      freq_minimum=freq_minimum,save_env=save_env,impulse=True,
                                                      window=window)
title=f"{str(min(tr.stats.starttime for tr in st))[:13]} to {str(max(tr.stats.endtime for tr in st))[:13]} \n Max cross-correlation Between Traces from a {ws}s rms envelope |\n between {freq_minimum}-{freq_maximum} Hz | max attempted shift = ±{shift/20}s"

heat_plot(corr_matrix,label='Max cross-correlation',title=title,annotate=False)

#Plotting shift max
shift_matrix = df_results.pivot(index="trace1", columns="trace2", values="lag")
title=f"{str(min(tr.stats.starttime for tr in st))[:13]} to {str(max(tr.stats.endtime for tr in st))[:13]} \n Shift for max cross-correlation between Traces from a {ws}s rms envelope, between {freq_minimum}-{freq_maximum} Hz |\n max attempted shift = ±{shift/20}s"
heat_plot(shift_matrix,label='Shift to give max cc [s]',title=title,cmap='cividis')

# %% testing indicudla cross correlation

def plot_cc(trace1_label, trace2_label):
        
    fig, axs = plt.subplots(1, 3, figsize=(30, 5))
    
    axs = np.flat(axs)
    ax = axs[0]
    row = df_results[(df_results.trace1==trace1_label) & (df_results.trace2==trace2_label)].iloc[0]
    cc = row["cc"]
    lags = (np.arange(len(cc)) - len(cc)//2) / 20  # / sample rate for time units
    ax.plot(lags, cc)
    ax.axvline(row["lag"], color="red", linestyle="--", label=f"max @ {row['lag']:.2f}s")
    ax.set_xlabel("Lag (s)")
    ax.set_ylabel("CC")
    ax.legend()
    
    #write this tommorow
    # for i in range(1,3):
    #     tr = st[0]
        
    #     t = tr.times()  # Time in seconds relative to trace start
    #     ax=axs[0]
    #     ax.plot(t, tr.data, color='red')
    #     ax.grid()
    #     ax.set_title('Raw')
    #     ax.set_xlabel('Seconds since trigger (s)',fontsize=15)
    #     ax.set_ylabel('Counts')
    # plt.title(f"{trace1_label} vs {trace2_label}")

idx = -1
trace1 = st_wind[idx].id+str(st_wind[idx].stats.starttime)[:13]
for tr in st_wind:
    trace2 = tr.id+str(tr.stats.starttime)[:13] 
    plot_cc(trace1,trace2)
    plt.show()



# %% Now i want to plot compared to 1 signal
st = read('data/galapagos/mermaid*/*identified/sac/m20*.20150120*.sac')
st_base,st1 = envelope_and_inpulse(st,ws,shift= shift,freq_maximum=freq_maximum,freq_minimum=freq_minimum,
                                         normalise=True,impulse=False)
tr_base = st_base[0]
st = read('data/galapagos/mermaid*/*identified/sac/m*.20150120*.sac')
st.remove(st[2])
st_eall,st = envelope_and_inpulse(st,ws,shift= shift,freq_maximum=freq_maximum,freq_minimum=freq_minimum,
                                         normalise=True)
n = len(st_eall)-1


for tr_e in st_eall:
    fig, ax = plt.subplots(figsize=(10, 5))


    ax.plot(tr_e.times(), tr_e.data, "b-")
    ax.plot(tr_base.times(),-tr_base.data,'k')
    fig.autofmt_xdate()
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('normalised counts')
    ax.tick_params(axis='y', labelleft=False)
    ax.set_title(f'M{tr_e.stats.station}.{str(tr_e.stats.starttime)[:10]} trace and envelope vs M{tr_base.stats.station}.{str(tr_base.stats.starttime)[:10]}')
    ax.axhline(y=0,color='k',linewidth=0.3)
    plt.show()
    # fig.savefig(f'/home/gregory/Documents/mermaid_glap/Plots/Show_jessica/09-03_meeting/M{tr_e.stats.station}.{str(tr_e.stats.starttime)[:10]}_env.png', dpi=100, bbox_inches='tight')

# %% corss correlate
st = read('data/galapagos/mermaid*/*identified/sac/m*.20150323T04*.sac')

ws=3
shift=2000
freq_maximum=5
freq_minimum=0.5
save_env=False
corr_matrix,df_results,st_e,st_wind = cross_correlate(st,ws=ws,shift=shift,freq_maximum=freq_maximum,
                                                      freq_minimum=freq_minimum,save_env=save_env)
title=f"{str(min(tr.stats.starttime for tr in st))[:13]} to {str(max(tr.stats.endtime for tr in st))[:13]} \n Max cross-correlation Between Traces from a {ws}s rms envelope |\n between {freq_minimum}-{freq_maximum} Hz | max attempted shift = ±{shift/20}s"

heat_plot(corr_matrix,label='Max cross-correlation',title=title,annotate=False)

#Plotting shift max
shift_matrix = df_results.pivot(index="trace1", columns="trace2", values="lag")
title=f"{str(min(tr.stats.starttime for tr in st))[:13]} to {str(max(tr.stats.endtime for tr in st))[:13]} \n Shift for max cross-correlation between Traces from a {ws}s rms envelope, between {freq_minimum}-{freq_maximum} Hz |\n max attempted shift = ±{shift/20}s"
heat_plot(shift_matrix,label='Shift to give max cc [s]',title=title,cmap='cividis')

df_results.sort_values('starttime')

