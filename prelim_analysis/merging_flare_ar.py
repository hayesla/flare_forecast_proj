import pandas as pd 
import matplotlib.pyplot as plt 
from sunpy.coordinates import frames
import sunpy.map
from astropy import units as u 
import datetime
from sunpy.net import Fido, attrs as a
import numpy as np 
import warnings
import seaborn as sns
import scipy.stats
warnings.filterwarnings("ignore")

flare_list = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/goes_flare_list/final_flare_list.csv")
# flare_list = flare_list.set_index(pd.to_datetime(flare_list["event_starttime"]))
# flare_list.sort_index(inplace=True)
flare_list["event_starttime"] = pd.to_datetime(flare_list["event_starttime"])

# for flares in which cross midnight to next day
flare_list.loc[(pd.to_datetime(flare_list.event_endtime)<flare_list.event_starttime),'event_endtime']=pd.to_datetime(flare_list["event_endtime"]) + datetime.timedelta(days=1)
flare_list.loc[(pd.to_datetime(flare_list.event_peaktime)<flare_list.event_starttime),'event_peaktime']=pd.to_datetime(flare_list["event_peaktime"]) + datetime.timedelta(days=1)

flare_list = flare_list.drop_duplicates(subset="event_peaktime")

flare_list["noaa_ar"] = flare_list["noaa_ar"].replace(["\n","", "     "], 0)
flare_list["noaa_ar"] = flare_list["noaa_ar"].astype(int)

flare_list["matchtime"] = flare_list["event_starttime"].dt.strftime("%Y-%m-%d 00:30")
#flare_list = flare_list[flare_list["noaa_ar"]!=0]


ar_data = pd.read_csv("/Users/laurahayes/ml_project_flares/flare_analysis/AR_analysis/SRS_all_2010-2018.csv")
ar_data = ar_data[ar_data["ID"].isin(["I"])]
ar_data["matchtime"] = ar_data["date"]
ar_data["noaa_ar"] = ar_data["Number"]

flare_ar_df = pd.merge(flare_list, ar_data, how="left", on=["matchtime", "noaa_ar"])

flare_ar_df = flare_ar_df.dropna()


unique_ar = flare_ar_df["noaa_ar"].unique()
events = []
for ar in unique_ar:
    unique_df = flare_ar_df[flare_ar_df.noaa_ar.isin([ar])]
    event = {}
    event["ar_num"] = ar
    event["max_flare"] = np.max(unique_df["goes_class_val"])
    event["max_area"] = np.max(unique_df["Area"])
    event["ar_class_max"] = unique_df.iloc[np.argmax(unique_df["goes_class_val"])]["Mag Type"]
    events.append(event)


events = pd.DataFrame(events)

events = events[events.max_area>0]

order = ['Alpha', 'Beta', 'Beta-Gamma',  'Beta-Delta',  'Beta-Gamma-Delta']
sns.scatterplot(data=events, x="max_area", y="max_flare", hue="ar_class_max", palette="magma", hue_order=order[::-1])
plt.xscale("log")
plt.yscale("log")


