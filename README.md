# Flare forcasting project

This repo consists of scripts for the data mining and analysis of flare events of the past solar cycle over the period
of 2010-01-01 -- 2018-12-31.

* in `goes_flare_list` codes are available for compiling the GOES XRS flare list

* in `cme_lists` the LASCO CDAW CME catalog is compiled. 
  * the CDAW catalog as a txt file is read and then the linked txt file for each event is also queried to determine the quality index
