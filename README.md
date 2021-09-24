# Flare forcasting project

This repo consists of scripts for the data mining and analysis of flares over the past two solar cycles from Aug 1996 - Dec 2018. The idea here is to test and develop several dataframes that can be used to build flare forecasting prediction models, particularly from a machine learning approach. 

The main aim is to develop a comprehensive flare list, and a database of active region characteristics over the past two solar cycles. To do this, the flare list from NOAA GOES/XRS is scraped, and collated with the daily NOAA SRS active region summary files. Furthermore, for solar cycle 24, the flare positions are scraped from the LMSAL latest events archive. We also look to create a flare-CME database through cross-referencing with the LASCO/SOHO CDAW CME list. 

The repo is divided into 5 directories:

* `AR_analysis` - which contains code to scrape the NOAA SRS files for the daily active region properties over a given time period. 
* `goes_flare_list` - which contains the code to get the solar flare list from the SWPC daily reports, and also has some code to test the flarelists availabe from several other sources
* `cme_lists` - which contains the codes to scrape the CDAW LASCO/SOHO CME list
* `prelim_analysis` - scripts to do exploratory data analysis, merging lists together, cme tests etc
* `forecast_tests` - which includes codes to develop flare rates and ML forecasts and estimate metrics. 
* `databases` - contains compiled CSV files of several different dataframes of different lists



Here's a plot of the locations of the flares from the past solar cycle and their positons!

<img src="https://user-images.githubusercontent.com/4620298/115426340-5120d680-a1f8-11eb-9917-f58615a68213.png" width="400" height="400" alt="centered image"/>

This repo will continue to change so be warned! If you have any questions, or any issues please reach out :)