import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 

"""
This script takes a GOES flare list that has been created using `final_flare_pos.py` and an AR list
created using `get_ar_data.py` and merges them to create a flare list that then includes AR data associated with each flare.
You can also merge it the other way if you like to create an AR database (for each day) with associated flares. 

It outputs a csv file of the merged flare and AR propery list.
"""


## read in flarelist
flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/final_flare_list.csv")
# create a column "matchtime" which will be used to merge with the AR data
flare_list["matchtime"] = pd.to_datetime(flare_list["event_starttime"], format="%Y-%m-%d %H:%M:%S").dt.strftime("%Y-%m-%d 00:30")

# tidying up some other columns (i.e. make AR num a string, and sort out dates of start, peak and end of flare)
flare_list["noaa_ar"] = flare_list["noaa_ar"].astype(str)


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
merged_db["noaa_ar"] = merged_db["noaa_ar"].replace(["\n","", "     "], 0)
merged_db.drop_duplicates(subset="event_peaktime", keep="last", inplace=True)
merged_db.reset_index(inplace=True, drop=True)
merged_db.to_csv("final_ar_flare_list.csv", index_label=False)