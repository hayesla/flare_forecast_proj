import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 

"""
This script takes a GOES flare list that has been created using `swpc_report_flarelist.py` and an AR list
created using `get_ar_data.py` and merges them to create a flare list that then includes AR data associated with each flare.
You can also merge it the other way if you like to create an AR database (for each day) with associated flares. 

It outputs a csv file of the merged flare and AR propery list.
"""


## read in flarelist
flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/swpc_event_list.csv")
# create a column "matchtime" which will be used to merge with the AR data
flare_list["matchtime"] = pd.to_datetime(flare_list["ts"], format="%Y%m%d%H%M").dt.strftime("%Y-%m-%d 00:30")

# tidying up some other columns (i.e. make AR num a string, and sort out dates of start, peak and end of flare)
flare_list["noaa_ar"] = flare_list["noaa_ar"].astype(str)
flare_list["event_starttime"] = pd.to_datetime(flare_list["date"].astype(str) + flare_list["start_time"].astype(str).str.zfill(4))
flare_list["event_peaktime"] = pd.to_datetime(flare_list["date"].astype(str) + flare_list["max_time"].astype(str).str.zfill(4))
flare_list["event_endtime"] = pd.to_datetime(flare_list["date"].astype(str) + flare_list["end_time"].astype(str).str.zfill(4))
# drop unneccessary columns
flare_list.drop(["start_time", "max_time", "end_time", "event_no", "ts"], axis=1, inplace=True)


# read in active region list
ar_data = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/SRS_all_2010-2018.csv")
# pull out only the data of interest (i.e. regions with sunspots marked with ID="I" from SRS)
ar_data = ar_data[ar_data["ID"].isin(["I"])]
# similarly create a "matchtime" columns
ar_data["matchtime"] = ar_data["date"]
# rename AR column so that it can be merged with GOES flare list
ar_data["noaa_ar"] = ar_data["Number"].astype(str)
ar_data.rename(columns={"date":"AR issue_date"}, inplace=True)


## merge the files!
merged_db = pd.merge(flare_list, ar_data, how="left", on=["matchtime", "noaa_ar"])
merged_db.to_csv("ar_flare_list.csv", index_label=False)