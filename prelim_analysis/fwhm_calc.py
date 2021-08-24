import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import glob
from sunpy import timeseries as ts
import datetime

""" -------------------------------------"""
# read in flarelist
flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/final_flare_list.csv")
flare_list["event_starttime"] = pd.to_datetime(flare_list["event_starttime"])
flare_list["event_endtime"] = pd.to_datetime(flare_list["event_endtime"])
flare_list["tt"] = [x.total_seconds() for x in flare_list.event_starttime - flare_list.event_starttime[0]]

# for flares in which cross midnight to next day
flare_list.loc[(pd.to_datetime(flare_list.event_endtime)<flare_list.event_starttime),'event_endtime']=pd.to_datetime(flare_list["event_endtime"]) + datetime.timedelta(days=1)
flare_list.loc[(pd.to_datetime(flare_list.event_peaktime)<flare_list.event_starttime),'event_peaktime']=pd.to_datetime(flare_list["event_peaktime"]) + datetime.timedelta(days=1)

# drop duplicate records
flare_list = flare_list.drop_duplicates(subset="event_peaktime")

#tidy up AR numbers
flare_list["noaa_ar"] = flare_list["noaa_ar"].replace(["\n","", "     "], 0)
flare_list["noaa_ar"] = flare_list["noaa_ar"].astype(int)

# add column to match with AR data
flare_list["matchtime"] = flare_list["event_starttime"].dt.strftime("%Y-%m-%d 00:30")

# fix integrated flux
flare_list["integrated_flux"] = flare_list["integrated_flux"].replace(['',"", "       "], 0).astype(float)

flare_list.reset_index(inplace=True, drop=True)
""" -------------------------------------"""


data_dir = '/Users/laurahayes/QPP/stats_study/TEBBS/goes_rawdata/'

def get_fwhm(flare_list, i):
    """
    Function to calculate the FWHM for each flare


    """
    tstart = flare_list.iloc[i]["event_starttime"]
    tend = flare_list.iloc[i]["event_endtime"]

    file_s = tstart.strftime("*%Y%m%d.fits")
    file_e = tend.strftime("*%Y%m%d.fits")


    if file_s == file_e:
        goes = ts.TimeSeries(data_dir + file_s)
    else:
        goes = ts.TimeSeries(data_dir + file_s, data_dir + file_e, concatenate=True)


    goes_flare = goes.truncate(tstart-datetime.timedelta(minutes=5), tend+datetime.timedelta(minutes=20))

    gl = goes_flare.to_dataframe()["xrsb"]
    gs = goes_flare.to_dataframe()["xrsa"]

    peak_half = gl[0] + (np.max(gl) - gl[0])/2 
    
    fwhm = gl[gl > peak_half]
    fwhm_s = min(fwhm.index)
    fwhm_e = max(fwhm.index)

    fwhm_seconds = (fwhm_e - fwhm_s).total_seconds()
    return fwhm_seconds

import time
t1 = time.time()

errors = []
fwhm_list = []
for i in range(len(flare_list)):
    print("{:d} out of {:d}".format(i, len(flare_list)))
    try:
        fwhm = get_fwhm(flare_list, i)
        fwhm_list.append(fwhm)
    except:
        print("error", i)
        fwhm_list.append(np.nan)
        errors.append(i)

t2 = time.time() - t1
print("it took {:f} seconds".format(t2))
flare_list["fwhm"] = fwhm_list

flare_list["dur_full"] = [x.total_seconds() for x in pd.to_datetime(flare_list["event_endtime"]) - pd.to_datetime(flare_list["event_starttime"])]
#  flare_list.to_csv("flare_list_w_fwhm.csv", index_label=False)

flare_list2 = flare_list[flare_list["fwhm"]>0]

flare_x = flare_list2[flare_list2["goes_class_ind"].isin(["X"])]
flare_m = flare_list2[flare_list2["goes_class_ind"].isin(["M"])]
flare_c = flare_list2[flare_list2["goes_class_ind"].isin(["C"])]


        
        