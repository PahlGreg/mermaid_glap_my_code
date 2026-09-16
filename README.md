# mermaid_glap_my_code
Code to analyses mermaid data on the galapagos but shoudl work for other mermaid data just change all the reads and other commands may not work

Contained within code are
Quick Commands to plot:
- spec_plot: Plot single spectragram (first in the time) by date and hour
- spec_plot_multi: Plot multiple spectograms from data within timeframe
- import_iris_data: import data from an online db at same time as a trace and adds to the stream
- trigger_loc: plots the location of mermaid triggers within a timeframe
- (not a command but simple code) event_search: makes stream of events with certian criteria and plots seismogram 

General code
  - plot_mer + function file 
    - Plots seismograms
    - filtered seismogreams
    - taup arrivals
    - spectrograms with all options
    - use for saving a bunch of plots create from traces
  - Data_invst_mer + functions: visualising the identified record with 
    - reads st into a pandas df adding region
    - Plots histograms of mag & gcarc of the record
    - Maps mermaid identified trigger location with bathymotry (currently does unidentified)
    - Same map but colour coded by tigger days and can set a timeperiod
    - table produced on days with >3 readings on 1 mermaid
  - Unidentified_mer: visualising the unidentified record uses some function form data_invst
    - reads into pd dataframe
    - determines days with >2 triggers per mermaid
    - map location fo trigger with data
    - Seismograms of unidentified
    - Table of mermaids that trigged within 10m of each other on unidentified signals
    - spectograms of unidentified
    - Stat plot of no triggers per mermaid
  - analys_20s_p1: code to analyise the periodic 20s high freqency signal indentified in record:
    - Makes section plots (option to trim amplitude to max within a timeframe)
    - Function to find the max peaks within a timeframe
    - cross correlates headtmap and other plots to analyse resulty
    - Plot map with amplitudes on to analyse spacial
  - space_time_plot: Takes Fredricks idea of 3 plots to analyse the time domain of array, spacially (done on qgis), havent done the last by combining the 2 into a score
    - uses the catagorises already contained in folders and reads names to create clasified stream
    - plots timeline of classification with symbols 
  - For the spacedomain Making_QGIS_GEOJSON does that then you can put into QGIS and add the converted to csv labelled st
