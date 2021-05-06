import pandas as pd 
from flarelist_utils import read_swpc_reports, read_ngdc_goes_reports
import glob 
import numpy as np 

# SWPC flare list
swpc_flares = pd.read_csv("swpc_event_list.csv")
swpc_flares["datetime"] = pd.to_datetime(swpc_flares["ts"], format="%Y%m%d%H%M")
matchstring = "gev_%Y%m%d_%H%M"
swpc_flares["EName"] = swpc_flares["datetime"].dt.strftime(matchstring)
swpc_flares["match_time"] = swpc_flares.datetime.dt.strftime("%Y-%m-%d %H:%M")
swpc_flares = swpc_flares.set_index("datetime")
swpc_flares["noaa_ar"] = swpc_flares["noaa_ar"].replace(["\n","", "     "],  "")
swpc_flares.sort_index(inplace=True)
#swpc_flares = swpc_flares.truncate("2010-05-01", "2016-12-31")

## HELIO flares
helio_flarelist = pd.read_csv("full_sswlatest.csv")
helio = helio_flarelist[helio_flarelist["goes_class_ind"].isin(["X", "M", "C"])]
helio["datetime"] = pd.to_datetime(helio["time_start"])
helio["match_time"] = helio.datetime.dt.strftime("%Y-%m-%d %H:%M")
helio = helio.drop_duplicates(subset="match_time")
helio = helio[helio["goes_class_ind"].isin(["X", "M", "C"])]
helio = helio.set_index("datetime")
helio.sort_index(inplace=True)
#helio = helio.truncate("2010-05-01", "2016-12-31")

### NGDC flares
ngdc_files = glob.glob("./goes_files/*goes-xrs*"); ngdc_files.sort()
ngdc_test = read_ngdc_goes_reports(ngdc_files[0])
for f in ngdc_files[1:]:
    df = read_ngdc_goes_reports(f)
    ngdc_test = ngdc_test.append(df)


ngdc_test["ts"] = ngdc_test.date + ngdc_test.start_time
ngdc_test.drop_duplicates(subset="ts")
ngdc_test["datetime"] = pd.to_datetime(ngdc_test["date"] + ngdc_test["start_time"])
ngdc_test["match_time"] = ngdc_test.datetime.dt.strftime("%Y-%m-%d %H:%M")

ngdc_test = ngdc_test.set_index("datetime")
ngdc_test = ngdc_test[ngdc_test["goes_class_ind"].isin(["X", "M", "C"])]
ngdc_test["noaa_ar"] = ngdc_test["noaa_ar"].replace(["\n","", "     "],  "")
ngdc_test.sort_index(inplace=True)
#ngdc_test = ngdc_test.truncate("2010-05-01", "2016-12-31")
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
        ar_no.append(np.nan)
    elif (len(aa)==1) or (len(aa)==3):
        pos_hgs.append(aa[0])
        ar_no.append(np.nan)
    elif len(aa)==4:
        pos_hgs.append(aa[0])
        ar_no.append("1"+aa[2])
    else:
        print("wahh?")


flare_pos["position_hgs"] = pos_hgs
flare_pos["ar_noaanum_latest"] = ar_no
flare_pos["ar_noaanum_latest"] = flare_pos["ar_noaanum_latest"].replace(["1?", "1??"],  np.nan)
flare_pos = flare_pos.drop(columns=["position"])


flare_pos["ar_noaanum_latest"] = flare_pos["ar_noaanum_latest"].astype(float)


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



merged_test = pd.merge(helio, flare_pos, left_on="ename", right_on= "EName")

## HELIO has the best data (most consistent with SWPC)




