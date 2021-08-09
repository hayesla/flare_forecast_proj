import pandas as pd 
import matplotlib.pyplot as plt 
import numpy as np 

## read in flarelist
flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/final_flare_list.csv")
# create a column "matchtime" which will be used to merge with the AR data
flare_list["matchtime"] = pd.to_datetime(flare_list["event_starttime"], format="%Y-%m-%d %H:%M:%S").dt.strftime("%Y-%m-%d 00:30")

# tidying up some other columns (i.e. make AR num a string)
flare_list["noaa_ar"] = flare_list["noaa_ar"].astype(str)

# only choose flaresthat have an associated AR
flare_list = flare_list[flare_list["noaa_ar"] != "     "]

# only want these columns
flare_list_df = flare_list[["matchtime", "goes_class_ind", "noaa_ar"]]
flare_list_df.reset_index(inplace=True, drop=True)

# we want new columns that include number of X, C and M class flares
flare_inds = pd.get_dummies(flare_list_df["goes_class_ind"])
flare_list_df = flare_list_df.merge(flare_inds, left_index=True, right_index=True)#.drop(columns="goes_class_ind")
flare_list_df["C+"] = flare_list_df["C"] + flare_list_df["M"] + flare_list_df["X"]
flare_list_df["M+"] = flare_list_df["M"] + flare_list_df["X"]
flare_list_df["X+"] = flare_list_df["X"]

# want flares per day
flare_list_df = flare_list_df.groupby(["matchtime", "noaa_ar"]).sum().reset_index()

## AR data
# read in active region list
ar_data = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/SRS_all_2010-2018.csv")
# pull out only the data of interest (i.e. regions with sunspots marked with ID="I" from SRS)
ar_data = ar_data[ar_data["ID"].isin(["I"])] # could also look for "IA" active regions to include more flares
# similarly create a "matchtime" columns
ar_data["matchtime"] = ar_data["date"]
# rename AR column so that it can be merged with GOES flare list
ar_data["noaa_ar"] = ar_data["Number"].astype(str)
ar_data.rename(columns={"date":"AR issue_date"}, inplace=True)

merged_db = pd.merge(ar_data, flare_list_df, how="left", on=["matchtime", "noaa_ar"])

## some flares left our as AR not defined yet. For example - an active region may come on disk and flare before 00:30 next day where its defined.
merged_db_ff = merged_db[merged_db["X+"].notnull()]
merged_db_test = merged_db_ff[flare_list_df.columns]
left_flares = pd.concat([flare_list_df, merged_db_test]).drop_duplicates(keep=False)

merged_db.replace(np.nan, 0, inplace=True)
ordered_cols = ['AR issue_date', 'noaa_ar', 'Carrington Longitude', 'Area', 'Z', 'Longitudinal Extent', 
			    'Number of Sunspots', 'Mag Type', 'Latitude', 'Longitude', 
			    'C', 'M', 'X', 'C+', 'M+', 'X+']

merged_db = merged_db[ordered_cols]
merged_db.rename(columns={"Z":"McIntosh"}, inplace=True)


merged_db.to_csv("ar_flare_ml_df.csv", index_label=False)