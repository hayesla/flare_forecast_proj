import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime

"""
This script creates three different dataframes which consists of different variations of merging 
solar flare data together with AR data.

* the swpc flare data (`swpc_flarelist_19960731_20181231.csv`) is generated in 
  generate_flarelist.py located in /flare_analysis/goes_flare_list/
* the NOAA active region data is `SRS_data_new_19960101_20181231.csv` that is 
  created by new_read_srs.py located in /flare_analysis/AR_analysis/.

It generates 

* `flare_AR_23_24.csv` - flare list with associated ARs information (length is length of flare list)

* `AR_flare_ml_23_24.csv` - daily ARs and whether there was a flare or not etc (length is length of AR list)

* `AR_flare_ml_23_24_evol.csv` - same as AR_flare_ml_23_24.csv with extra columns for the evolution (i.e. what was the mag class of previous day etc.)
"""

## read in the SWPC flarelist
flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/swpc_flarelist_19960731_20181231.csv")

# create a column "matchtime" which will be used to merge with the AR data
flare_list["matchtime"] = pd.to_datetime(flare_list["start_time"], format="%Y-%m-%d %H:%M:%S").dt.strftime("%Y-%m-%d 00:30")

# tidying up some other columns (i.e. make AR num a string, and sort out dates of start, peak and end of flare)
flare_list["noaa_ar"] = flare_list["noaa_ar"].astype(str)

#  only choose flaresthat have an associated AR
flare_list = flare_list[~flare_list["noaa_ar"].isin(["0"])]

#  only want these columns
flare_list_df = flare_list[["matchtime", "goes_class_ind", "noaa_ar", "goes_class"]]
flare_list_df.reset_index(inplace=True, drop=True)

# we want new columns that include number of X, C and M class flares, and also the X+, M+, and C+
flare_inds = pd.get_dummies(flare_list_df["goes_class_ind"])
flare_list_df = flare_list_df.merge(flare_inds, left_index=True, right_index=True)  # .drop(columns="goes_class_ind")
flare_list_df["C+"] = flare_list_df["C"] + flare_list_df["M"] + flare_list_df["X"]
flare_list_df["M+"] = flare_list_df["M"] + flare_list_df["X"]
flare_list_df["X+"] = flare_list_df["X"]

# want flares per day
flare_list_df_for_ml = flare_list_df.groupby(["matchtime", "noaa_ar"]).sum().reset_index()


# AR data
# read in active region list
ar_data = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/SRS_data_new_19960101_20181231.csv")
#  similarly create a "matchtime" columns - sometimes hours are slightly off so fix here
ar_data["date"] = pd.to_datetime(ar_data["date"]).dt.strftime("%Y-%m-%d 00:30")
ar_data["matchtime"] = ar_data["date"]
# rename AR column so that it can be merged with GOES flare list
ar_data["noaa_ar"] = ar_data["ar_noaanum"].astype(str)
ar_data.drop(columns=["NM", "NONE", "BETA"], inplace=True)
ar_data.rename(columns={"date": "AR issue_date"}, inplace=True)
# adjust to match the timerange of the start of solar cycle 23 (this is what the flare list timerange is)
ar_data = ar_data[ar_data["matchtime"]>="1996-08-01"]
ar_data.reset_index(inplace=True, drop=True)


def get_lat_long(location):
    """
    Given the location as 'N11W06" - this function extract the lat and long values

    Parameters
    ----------
    location : `~str`
        location on solar disk in heliographic stonyhurst
    
    Returns
    -------
    latitude: `~int`
        latitude coordinate point
    longitude: `~int`
        longitude coordinate point
    """
    location_dict = {"S":-1, "N":1, "E":-1, "W":1}
    latitude = location[0:3]
    longitude = location[3:]

    latitude = location_dict[latitude[0]]*int(latitude[1:])
    longitude = location_dict[longitude[0]]*int(longitude[1:])
    
    return latitude, longitude

# add to the dataframe
lat_val, long_val = [], []
for i in range(len(ar_data)):
    latt, longg = get_lat_long(ar_data["LOCATION"].iloc[i])
    lat_val.append(latt)
    long_val.append(longg)

ar_data["Latitude"] = lat_val
ar_data["Longitude"] = long_val


## Merge for flare list with AR properties & save to file
merged_db_flares = pd.merge(flare_list_df, ar_data, how="left", on=["matchtime", "noaa_ar"])
merged_db_flares.to_csv("flare_AR_23_24.csv", index_label=False)

## Merge for AR ML frame
merged_db_ar = pd.merge(ar_data, flare_list_df_for_ml, how="left", on=["matchtime", "noaa_ar"])

## replace nan's with 0's
merged_db_ar.replace(np.nan, 0, inplace=True)

## reorder columns
ordered_cols = ['AR issue_date', 'noaa_ar', 'Carrington_long', 'AREA', 'Z', 'Longitude_extent',
				'Latitude', 'Longitude',
                'No_sunspots', 'MAGTYPE', 'LOCATION',
                'C', 'M', 'X', 'C+', 'M+', 'X+']

merged_db_ar = merged_db_ar[ordered_cols]
merged_db_ar.rename(columns={"Z": "McIntosh"}, inplace=True)

# save this dataframe - this is the main dataframe.
merged_db_ar.to_csv("AR_flare_ml_23_24.csv", index_label=False)

def grow_dataframe(data):
    """
    Add in some extra features from the previous data.
    """
    prev_area, prev_mcint, prev_mag, prev_flare = [], [], [], []
    for i in range(len(data)):

        test = data.iloc[i]
        previous_day = (pd.to_datetime(test["AR issue_date"])-datetime.timedelta(days=1)).strftime("%Y-%m-%d 00:30")
        ar_match = test["noaa_ar"]
        data_prev = data[(data["AR issue_date"].isin([previous_day]))&(data["noaa_ar"].isin([ar_match]))]

        if len(data_prev)==0:
            prev_area.append(np.nan), prev_mcint.append(np.nan), prev_mag.append(np.nan), prev_flare.append(np.nan)
        else:
            prev_area.append(data_prev["AREA"].values[0]), prev_mcint.append(data_prev["McIntosh"].values[0]), 
            prev_mag.append(data_prev["MAGTYPE"].values[0]), prev_flare.append(data_prev["C+"].values[0])
           

    data["pre_area"] = prev_area
    data["pre_mcint"] = prev_mcint
    data["pre_mag"] = prev_mag
    data["pre_flare"] = prev_flare

    return data
## add in previous day data as extra columns - e.g. add in McIntosh of prior day etc.
merged_db_ar_withprior = grow_dataframe(merged_db_ar)
merged_db_ar_withprior.to_csv("AR_flare_ml_23_24_evol.csv", index_label=False)


## Testing flares.
## some flares left our as AR not defined yet. 
## For example - an active region may come on disk and flare before 00:30 next day where its defined.
# merged_db_ff = merged_db_ar[merged_db_ar["X+"].notnull()]
# merged_db_test = merged_db_ff[flare_list_df_for_ml.columns]
# left_flares = pd.concat([flare_list_df_for_ml, merged_db_test]).drop_duplicates(keep=False)
