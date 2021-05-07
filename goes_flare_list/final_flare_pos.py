import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
from sunpy.net import Fido, attrs as a 
from sunpy.coordinates import frames
from astropy.coordinates import SkyCoord
from astropy import units as u 


"""
This is the script that creates the final flare list used in this work. 
It uses the SWPC flare list created in `swpc_report_flarelist.py` and then merges
this flare list with the LMSAL event summary data which is scrapped using `get_flare_positions.py`.
The final flarelist saved is named `final_flare_list.csv`.
"""

## SWPC flare list
flares = pd.read_csv("swpc_event_list.csv")
flares["datetime"] = pd.to_datetime(flares["ts"], format="%Y%m%d%H%M")
matchstring = "gev_%Y%m%d_%H%M"
flares["EName"] = flares["datetime"].dt.strftime(matchstring)

## Get flare position list which was scraped from the LMSAL latest events
flare_pos = pd.read_csv("final_latestevents_scraping.csv")
pos = flare_pos["Derived Position"].replace(np.nan, '', regex=True) \
    + flare_pos["Derived Position (SECCHI/EUVI (BEACON) or EIT High Cadence Wavelength)"].replace(np.nan, '', regex=True)\
    + flare_pos["Derived Position (SECCHI/EUVI or EIT High Cadence Wavelength or SDO/AIA)"].replace(np.nan, '', regex=True)\
    + flare_pos["Derived Position (SECCHI/EUVI or EIT High Cadence Wavelength)"].replace(np.nan, '', regex=True)
flare_pos["position"] = pos
flare_pos = flare_pos.drop(columns=["Derived Position", "Derived Position (SECCHI/EUVI (BEACON) or EIT High Cadence Wavelength)", 
                "Derived Position (SECCHI/EUVI or EIT High Cadence Wavelength or SDO/AIA)", 
                "Derived Position (SECCHI/EUVI or EIT High Cadence Wavelength)"])

flare_pos.reset_index(inplace=True, drop=True)
pos_hgs = []
ar_no = []
for i in range(len(flare_pos)):
    aa = flare_pos["position"][i].split()
    if len(aa)==0:
        pos_hgs.append("")
        ar_no.append("")
    elif (len(aa)==1) or (len(aa)==3):
        pos_hgs.append(aa[0])
        ar_no.append("")
    elif len(aa)==4:
        pos_hgs.append(aa[0])
        ar_no.append("1"+aa[2])
    else:
        print("wahh?")

flare_pos["position_hgs"] = pos_hgs
flare_pos["ar_noaanum_latest"] = ar_no
flare_pos = flare_pos.drop(columns=["position"])

match_dict = {"S": -1, "N": 1, "E":-1, "W":1}
def get_latlon(x):
    try:
        lat = match_dict[x[0]]*int(x[1:3])
        lon = match_dict[x[3]]*int(x[4:6]) 
        return np.array([lat, lon])
    except:
        return np.array([np.nan, np.nan])

coord_hgs = np.vstack(flare_pos["position_hgs"].map(get_latlon))
flare_pos["hgs_lat"], flare_pos["hgs_lon"] = coord_hgs[:, 0], coord_hgs[:, 1]
flare_pos = flare_pos.drop(flare_pos[flare_pos["hgs_lat"].isnull()].index)
flare_pos.reset_index(inplace=True, drop=True)


merged = pd.merge(flares, flare_pos, how="left", on="EName")
excess_flares = flares[~flares["EName"].isin(merged["EName"])]

def get_goes_class(x):
    if x[0]=="C":
        return float(x[1:])*1e-6
    elif x[0] == "M":
        return float(x[1:])*(1e-5)
    elif x[0] == "X":
        return float(x[1:])*(1e-4)
    else:
        return

merged["goes_class_val"] = merged["goes_class"].map(get_goes_class)

merged["event_starttime"] = pd.to_datetime(merged["date"].astype(str) + merged["start_time"].astype(str).str.zfill(4))
merged["event_peaktime"] = pd.to_datetime(merged["date"].astype(str) + merged["max_time"].astype(str).str.zfill(4))
merged["event_endtime"] = pd.to_datetime(merged["date"].astype(str) + merged["end_time"].astype(str).str.zfill(4))

columns = ["event_starttime", "event_peaktime", "event_endtime", "goes_class_ind", 
           "goes_class", "goes_class_val", "integrated_flux", "noaa_ar", "position_hgs", 
           "hgs_lat", "hgs_lon"]

final_df = merged[columns]

## convert hgs to hpc coords
hgs_coords = SkyCoord(final_df["hgs_lon"]*u.deg, final_df["hgs_lat"]*u.deg, 
    frame=frames.HeliographicStonyhurst, obstime=final_df["event_starttime"])

hpc_coords = hgs_coords.transform_to(frames.Helioprojective(observer="earth"))
final_df["hpc_x"] = hpc_coords.Tx.value
final_df["hpc_y"] = hpc_coords.Ty.value

## save the final flare list
final_df.to_csv("final_flare_list.csv", index_label=False)
